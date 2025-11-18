"""
LiteLLM Model Router
Unified interface for multiple free AI models with failover
"""

import time
import logging
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from litellm import completion, acompletion
from litellm.exceptions import RateLimitError, APIError, Timeout, AuthenticationError

from .secrets_manager import get_secrets_manager
from .cache_manager import get_cache_manager


logger = logging.getLogger(__name__)


class ModelRouter:
    """
    Intelligent model router with failover support
    
    Features:
    - Multiple free models (Groq, Gemini, Mistral, HuggingFace)
    - Automatic failover on errors
    - Rate limit handling with jitter
    - Usage tracking
    - Response caching
    - Health scoring per provider
    - Credential validation via test pings
    - Graceful downgrade with heuristic guidance
    """
    
    def __init__(self):
        self.secrets = get_secrets_manager()
        self.cache = get_cache_manager()
        
        # Model priorities (fastest first)
        self.model_priority = [
            {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 8000,
                "speed": "fastest"
            },
            {
                "provider": "gemini",
                "model": "gemini-1.5-flash",
                "max_tokens": 8000,
                "speed": "very_fast"
            },
            {
                "provider": "mistral",
                "model": "mistral-large-latest",
                "max_tokens": 8000,
                "speed": "fast"
            }
        ]
        
        # Health scores for each provider (0-100, 100 = healthy)
        self.health_scores = {}
        self._load_health_scores()
        
        # Check which models are available
        self.available_models = self._check_available_models()
        
        if not self.available_models:
            logger.warning("No AI models configured! Please add API keys to .env file")
    
    def _load_health_scores(self):
        """Load persistent health scores from cache"""
        for model_config in self.model_priority:
            provider = model_config["provider"]
            cached_score = self.cache.cache_get(f"health_score_{provider}")
            self.health_scores[provider] = cached_score if cached_score is not None else 100
    
    def _save_health_score(self, provider: str, score: int):
        """Save health score to cache"""
        self.health_scores[provider] = max(0, min(100, score))  # Clamp to 0-100
        self.cache.cache_set(f"health_score_{provider}", self.health_scores[provider], expire=86400)  # 24 hours
        logger.debug(f"Health score for {provider}: {self.health_scores[provider]}")
    
    def _update_health_score(self, provider: str, success: bool):
        """Update health score based on request result"""
        current_score = self.health_scores.get(provider, 100)
        
        if success:
            # Gradually increase score on success (up to 100)
            new_score = min(100, current_score + 5)
        else:
            # Decrease score on failure
            new_score = max(0, current_score - 15)
        
        self._save_health_score(provider, new_score)
    
    def _check_available_models(self) -> List[Dict]:
        """Check which models have valid API keys with test pings"""
        keys_status = self.secrets.validate_model_keys()
        available = []
        
        for model_config in self.model_priority:
            provider = model_config["provider"]
            if keys_status.get(provider):
                # Validate with test ping
                if self._test_ping(model_config):
                    available.append(model_config)
                    logger.info(f"✓ {provider} is available and validated")
                else:
                    logger.warning(f"✗ {provider} API key exists but validation failed")
        
        logger.info(f"Available models: {[m['provider'] for m in available]}")
        return available
    
    def _test_ping(self, model_config: Dict) -> bool:
        """
        Test model availability with genuine credential validation
        
        Makes a lightweight completion call to verify credentials
        """
        provider = model_config["provider"]
        
        # Check cached validation (valid for 1 hour for success, 5 min for failure)
        cache_key = f"ping_validation_{provider}"
        cached = self.cache.cache_get(cache_key)
        if cached is not None:
            return cached
        
        # Get API key
        api_key = self.secrets.get(f"{provider.upper()}_API_KEY")
        if not api_key:
            logger.warning(f"{provider} API key not found")
            self.cache.cache_set(cache_key, False, expire=300)  # Cache failure for 5 min
            return False
        
        try:
            # Minimal test completion (3-5 tokens)
            test_messages = [{"role": "user", "content": "hi"}]
            
            model_name = model_config["model"]
            # Add provider prefix
            if provider == "gemini":
                model_name = f"gemini/{model_name}"
            elif provider == "groq":
                model_name = f"groq/{model_name}"
            elif provider == "mistral":
                model_name = f"mistral/{model_name}"
            
            # Make lightweight call with short timeout
            response = completion(
                model=model_name,
                messages=test_messages,
                max_tokens=3,
                api_key=api_key,
                timeout=5  # Short timeout to avoid blocking
            )
            
            # Success! Cache for 1 hour
            self.cache.cache_set(cache_key, True, expire=3600)
            logger.info(f"{provider} credentials validated successfully")
            return True
        
        except AuthenticationError as e:
            # Invalid/expired credentials
            logger.error(f"{provider} authentication failed - invalid or expired API key")
            self.cache.cache_set(cache_key, False, expire=300)  # Cache failure for 5 min
            self._save_health_score(provider, 0)  # Mark as unhealthy
            return False
        
        except Timeout:
            # Timeout - might be temporary, don't cache failure
            logger.warning(f"{provider} ping timeout - may be temporary")
            return False  # Don't cache - might be transient
        
        except Exception as e:
            # Other errors - might be temporary
            logger.warning(f"{provider} ping failed: {type(e).__name__} - {str(e)}")
            return False  # Don't cache - might be transient
    
    def _revalidate_providers(self):
        """Re-check availability of all providers (called periodically)"""
        logger.debug("Revalidating all providers...")
        
        for model_config in self.model_priority:
            provider = model_config["provider"]
            
            # Check if provider has API key
            api_key = self.secrets.get(f"{provider.upper()}_API_KEY")
            if not api_key:
                continue
            
            # If provider is not in available_models, try to add it back
            is_available = any(m["provider"] == provider for m in self.available_models)
            
            if not is_available:
                # Check cached ping result
                cache_key = f"ping_validation_{provider}"
                cached_ping = self.cache.cache_get(cache_key)
                
                # If we have a cached failure, respect it
                if cached_ping is False:
                    logger.debug(f"Skipping {provider} - cached validation failure (will retry after cache expires)")
                    continue
                
                # If no cached result or cached success, verify current credentials
                if cached_ping is None:
                    logger.info(f"Re-validating {provider} credentials...")
                    if not self._test_ping(model_config):
                        logger.warning(f"{provider} validation failed, not re-adding")
                        continue
                
                # Validation passed (cached or fresh) - add back to available models
                health_score = self.health_scores.get(provider, 100)
                logger.info(f"Re-adding {provider} to available models (health: {health_score})")
                self.available_models.append(model_config)
                
                # Only boost health if it's very low AND provider validated successfully
                if health_score < 30 and cached_ping is not False:
                    self._save_health_score(provider, 30)
                    logger.debug(f"Boosted {provider} health to 30 for recovery attempt")
    
    def _probe_unhealthy_provider(self, model_config: Dict) -> bool:
        """
        Lightweight probe for unhealthy providers to help them recover
        
        Returns True if provider responds successfully
        """
        provider = model_config["provider"]
        
        try:
            # Simple test with minimal resources
            test_messages = [{"role": "user", "content": "hi"}]
            
            result = self._call_model(
                model_config,
                test_messages,
                temperature=0.1,
                max_tokens=5
            )
            
            # Success! Update health score
            self._update_health_score(provider, success=True)
            logger.info(f"{provider} recovery probe succeeded - health restored")
            return True
        
        except Exception as e:
            logger.debug(f"{provider} recovery probe failed: {e}")
            return False
    
    def _quarantine_provider(self, provider: str, model_config: Dict):
        """
        Quarantine a provider due to authentication failure
        
        - Removes from available_models
        - Sets health score to 0
        - Caches validation failure for 5 minutes
        """
        # Remove from available models
        self.available_models = [m for m in self.available_models if m["provider"] != provider]
        
        # Set health to 0
        self._save_health_score(provider, 0)
        
        # Cache validation failure for 5 minutes
        cache_key = f"ping_validation_{provider}"
        self.cache.cache_set(cache_key, False, expire=300)  # 5 min quarantine
        
        logger.warning(f"{provider} quarantined for 5 minutes due to authentication failure")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Send chat completion request with automatic failover
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0 - 2.0)
            max_tokens: Max response tokens
            use_cache: Use cached responses if available
            retry_count: Number of retries per model
        
        Returns:
            Dict with 'content', 'model', 'tokens_used', 'time_taken'
        """
        if not self.available_models:
            return self._graceful_downgrade(messages, "no_models_configured")
        
        # Periodically revalidate providers (every ~10 requests via random sampling)
        if random.random() < 0.1:
            self._revalidate_providers()
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._generate_cache_key(messages, temperature)
            cached = self.cache.cache_get(cache_key)
            if cached:
                logger.info(f"Cache hit for request")
                return cached
        
        # Sort models by health score
        sorted_models = sorted(
            self.available_models,
            key=lambda m: self.health_scores.get(m["provider"], 100),
            reverse=True
        )
        
        # Try each model in priority order
        last_error = None
        errors_by_provider = {}
        
        for model_config in sorted_models:
            provider = model_config["provider"]
            health_score = self.health_scores.get(provider, 100)
            
            # If health score is very low, occasionally give it a chance to recover
            if health_score < 20:
                # 20% chance to try recovery probe
                if random.random() < 0.2:
                    logger.info(f"Attempting recovery probe for {provider} (health: {health_score})")
                    if self._probe_unhealthy_provider(model_config):
                        # Probe succeeded, continue with this provider
                        logger.info(f"{provider} recovered! Continuing with request")
                    else:
                        # Probe failed, skip to next
                        logger.warning(f"{provider} recovery failed, skipping")
                        continue
                else:
                    logger.debug(f"Skipping {provider} due to low health score: {health_score}")
                    continue
            
            for attempt in range(retry_count):
                try:
                    result = self._call_model(
                        model_config,
                        messages,
                        temperature,
                        max_tokens or model_config["max_tokens"]
                    )
                    
                    # Update health score on success
                    self._update_health_score(provider, success=True)
                    
                    # Cache successful response
                    if use_cache and result.get("content"):
                        cache_key = self._generate_cache_key(messages, temperature)
                        self.cache.cache_set(cache_key, result, expire=3600)  # 1 hour
                    
                    return result
                
                except RateLimitError as e:
                    logger.warning(f"{provider} rate limit hit, trying next model...")
                    last_error = self._map_provider_exception(provider, e)
                    errors_by_provider[provider] = last_error
                    self._update_health_score(provider, success=False)
                    break  # Skip to next model
                
                except AuthenticationError as e:
                    logger.error(f"{provider} authentication failed - quarantining for 5 minutes")
                    last_error = self._map_provider_exception(provider, e)
                    errors_by_provider[provider] = last_error
                    
                    # Quarantine this provider immediately
                    self._quarantine_provider(provider, model_config)
                    break  # Skip to next model - auth won't fix with retry
                
                except (APIError, Timeout) as e:
                    logger.warning(f"{provider} error (attempt {attempt+1}/{retry_count}): {e}")
                    last_error = self._map_provider_exception(provider, e)
                    errors_by_provider[provider] = last_error
                    
                    if attempt < retry_count - 1:
                        # Exponential backoff with jitter
                        backoff = (2 ** attempt) + random.uniform(0, 1)
                        logger.debug(f"Retrying {provider} after {backoff:.2f}s...")
                        time.sleep(backoff)
                    else:
                        self._update_health_score(provider, success=False)
                    continue
                
                except Exception as e:
                    logger.error(f"{provider} unexpected error: {e}")
                    last_error = self._map_provider_exception(provider, e)
                    errors_by_provider[provider] = last_error
                    self._update_health_score(provider, success=False)
                    break
        
        # All models failed - attempt graceful downgrade
        return self._graceful_downgrade(messages, last_error, errors_by_provider)
    
    def _map_provider_exception(self, provider: str, exception: Exception) -> str:
        """Map provider-specific exceptions to standardized error messages"""
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        # Provider-specific mappings
        if isinstance(exception, AuthenticationError):
            return f"{provider}: Invalid or expired API key"
        elif isinstance(exception, RateLimitError):
            return f"{provider}: Rate limit exceeded - try again later"
        elif isinstance(exception, Timeout):
            return f"{provider}: Request timeout - service may be slow"
        elif isinstance(exception, APIError):
            return f"{provider}: API error - {error_msg}"
        else:
            return f"{provider}: {error_type} - {error_msg}"
    
    def _graceful_downgrade(
        self,
        messages: List[Dict[str, str]],
        error: Optional[str],
        errors_by_provider: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Provide graceful downgrade when all models fail
        
        Returns cached or heuristic guidance instead of hard failure
        """
        # Try to find any cached response for similar requests
        cache_key = self._generate_cache_key(messages, temperature=0.7)
        cached = self.cache.cache_get(cache_key)
        
        if cached:
            logger.info("Using cached response as fallback")
            cached["fallback"] = True
            cached["fallback_reason"] = "All models unavailable - serving cached response"
            return cached
        
        # Generate heuristic guidance based on request
        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
        
        heuristic_response = self._generate_heuristic_guidance(user_message)
        
        # Log the failure details
        if errors_by_provider:
            logger.error(f"All models failed. Errors: {errors_by_provider}")
        
        return {
            "content": heuristic_response,
            "model": "heuristic_fallback",
            "tokens_used": 0,
            "time_taken": 0,
            "error": error or "all_models_failed",
            "fallback": True,
            "fallback_reason": "All AI models unavailable - providing heuristic guidance",
            "errors_by_provider": errors_by_provider or {}
        }
    
    def _generate_heuristic_guidance(self, user_message: str) -> str:
        """Generate heuristic guidance when no models are available"""
        # Basic heuristic responses for common patterns
        user_lower = user_message.lower()
        
        if "plan" in user_lower or "create" in user_lower or "build" in user_lower:
            return """I apologize, but all AI models are currently unavailable. 
            
For project planning, consider these general steps:
1. Define clear requirements and goals
2. Break down the project into smaller tasks
3. Choose appropriate technologies and frameworks
4. Create a basic project structure
5. Implement features incrementally
6. Test and iterate

Please try again in a few moments when the AI models are back online."""
        
        elif "error" in user_lower or "fix" in user_lower or "debug" in user_lower:
            return """I apologize, but all AI models are currently unavailable.

For debugging, try these general approaches:
1. Read error messages carefully
2. Check logs for detailed information
3. Verify your code syntax
4. Test components individually
5. Search documentation for similar issues

Please try again in a few moments when the AI models are back online."""
        
        else:
            return f"""I apologize, but all AI models are currently unavailable due to technical issues.

Your request: "{user_message[:100]}..."

Please try again in a few moments. If the issue persists, check:
- API key validity
- Network connectivity
- Service status of AI providers

The system will automatically retry when models become available."""
    
    def _call_model(
        self,
        model_config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call a specific model"""
        provider = model_config["provider"]
        model_name = model_config["model"]
        
        # Get API key
        api_key = self.secrets.get(f"{provider.upper()}_API_KEY")
        if not api_key:
            raise Exception(f"Missing API key for {provider}")
        
        start_time = time.time()
        
        # Prepare request
        request_params = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "api_key": api_key
        }
        
        # Special handling for different providers
        if provider == "gemini":
            request_params["model"] = f"gemini/{model_name}"
        elif provider == "groq":
            request_params["model"] = f"groq/{model_name}"
        elif provider == "mistral":
            request_params["model"] = f"mistral/{model_name}"
        
        # Make the call
        try:
            response = completion(**request_params)
            
            time_taken = time.time() - start_time
            
            # Extract response (type: ignore for litellm dynamic types)
            content = response.choices[0].message.content  # type: ignore
            
            # Safely extract token usage
            usage = getattr(response, 'usage', None)
            tokens_used = getattr(usage, 'total_tokens', 0) if usage else 0
            
            # Log usage
            self.cache.log_model_usage(
                provider=provider,
                model=model_name,
                tokens_used=tokens_used,
                request_time=time_taken,
                success=True
            )
            
            logger.info(f"✓ {provider} responded in {time_taken:.2f}s ({tokens_used} tokens)")
            
            return {
                "content": content,
                "model": f"{provider}/{model_name}",
                "tokens_used": tokens_used,
                "time_taken": round(time_taken, 3),
                "provider": provider
            }
        
        except Exception as e:
            # Log failed attempt
            self.cache.log_model_usage(
                provider=provider,
                model=model_name,
                tokens_used=0,
                request_time=time.time() - start_time,
                success=False
            )
            raise
    
    def _generate_cache_key(self, messages: List[Dict], temperature: float) -> str:
        """Generate cache key from request parameters"""
        import hashlib
        
        # Create deterministic string from messages
        messages_str = str(messages) + str(temperature)
        hash_obj = hashlib.md5(messages_str.encode())
        return f"chat_{hash_obj.hexdigest()}"
    
    def get_usage_stats(self, hours: int = 24) -> Dict:
        """Get usage statistics for all models"""
        return self.cache.get_model_stats(hours=hours)
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report for all providers
        
        Returns:
            Dict with health scores, availability, and status
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "providers": {},
            "overall_health": "healthy",
            "available_count": len(self.available_models),
            "total_count": len(self.model_priority)
        }
        
        total_score = 0
        for model_config in self.model_priority:
            provider = model_config["provider"]
            health_score = self.health_scores.get(provider, 100)
            is_available = any(m["provider"] == provider for m in self.available_models)
            
            total_score += health_score if is_available else 0
            
            # Determine status
            if not is_available:
                status = "unavailable"
            elif health_score >= 80:
                status = "healthy"
            elif health_score >= 50:
                status = "degraded"
            else:
                status = "critical"
            
            report["providers"][provider] = {
                "health_score": health_score,
                "available": is_available,
                "status": status,
                "model": model_config["model"]
            }
        
        # Overall health
        if len(self.available_models) == 0:
            report["overall_health"] = "critical"
        elif total_score / max(1, len(self.available_models)) < 50:
            report["overall_health"] = "degraded"
        
        return report
    
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Stream chat responses (for future TUI/CLI implementation)
        Currently not implemented - use chat() instead
        """
        # TODO: Implement streaming for CLI/TUI
        raise NotImplementedError("Streaming not yet implemented")


# Global instance
_model_router = None

def get_model_router() -> ModelRouter:
    """Get global model router instance"""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router

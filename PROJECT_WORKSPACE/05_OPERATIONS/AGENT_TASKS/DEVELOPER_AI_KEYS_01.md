# 🔑 Developer AI-Keys-01: Multi-Key Support

> **📍 المهمة**: تطبيق نظام Multi-Key Rotation لدعم مفاتيح متعددة لنفس ال Provider

**الأولوية**: 🔴🔴🔴🔴🔴 (حرجة - عالية جداً)  
**المدة المتوقعة**: 2-3 أيام  
**المتطلبات السابقة**: فهم `model_router.py` و `secrets_manager.py`  
**المخرجات**: نظام يدعم 3+ مفاتيح لكل provider مع تبديل تلقائي

---

## 📋 الهدف

تمكين المنصة من استخدام **multiple API keys** لنفس ال Provider (مثل 3 مفاتيح Groq) مع التبديل التلقائي عند انتهاء حد المفتاح الحالي.

### المشكلة الحالية

```python
# الوضع الحالي (❌):
GROQ_API_KEY = "sk-proj-xxx"  # مفتاح واحد فقط

# عند انتهاء حده (14,400 tokens):
→ ينتقل لـ Gemini (provider مختلف تماماً!)
→ لا يمكن استخدام Groq بقية اليوم ❌
```

### الحل المطلوب

```python
# الوضع الجديد (✅):
GROQ_API_KEY_1 = "sk-proj-AAA"  # Primary
GROQ_API_KEY_2 = "sk-proj-BBB"  # Backup
GROQ_API_KEY_3 = "sk-proj-CCC"  # Emergency

# عند انتهاء Key 1:
→ يتبدل تلقائياً إلى Key 2 ✅
→ نفس السرعة، نفس ال Provider ✅
→ لا انقطاع في الخدمة ✅
```

---

## 🎯 المخرجات المطلوبة

### ✅ Acceptance Criteria

1. ✅ **دعم مفاتيح متعددة**:
   - يجب أن يدعم النظام 1-10 مفاتيح لكل provider
   - كل مفتاح له: `id`, `key`, `priority`, `daily_limit`

2. ✅ **اختبار المفاتيح**:
   - جميع المفاتيح تُختبر عند البدء (test ping)
   - المفاتيح الفاشلة تُستبعد تلقائياً

3. ✅ **الاختيار الذكي**:
   - يُختار المفتاح بناءً على:
     - Priority (الأولوية)
     - Health Score
     - Quota المتبقي (Phase 2)

4. ✅ **التبديل التلقائي**:
   - عند فشل مفتاح → ينتقل للتالي فوراً
   - عند quarantine → يُستبعد مؤقتاً (5 دقائق)

5. ✅ **Backward Compatible**:
   - النظام القديم يجب أن يعمل (مفتاح واحد فقط)
   - `GROQ_API_KEY` (بدون رقم) = `GROQ_API_KEY_1`

---

## 📝 المهام التفصيلية

### Task 1: تعديل SecretsManager (1 يوم)

**الملف**: `ServerAutomationAI/dev_platform/core/secrets_manager.py`

#### 1.1 إضافة `get_provider_keys()`

```python
def get_provider_keys(self, provider: str) -> List[Dict[str, Any]]:
    """
    Get all keys for a specific provider
    
    Args:
        provider: "groq", "gemini", "mistral", etc.
    
    Returns:
        List of key configurations:
        [
            {
                "id": 1,
                "key": "sk-proj-xxx",
                "priority": 1,
                "daily_limit": 14400
            },
            {
                "id": 2,
                "key": "sk-proj-yyy",
                "priority": 2,
                "daily_limit": 14400
            }
        ]
    """
    keys = []
    provider_upper = provider.upper()
    
    # Try numbered keys first (_1, _2, _3, ...)
    i = 1
    while True:
        key_name = f"{provider_upper}_API_KEY_{i}"
        key_value = self.get(key_name)
        
        if not key_value:
            break  # No more keys
        
        # Get priority (default to index)
        priority = int(self.get(f"{provider_upper}_KEY_{i}_PRIORITY", str(i)))
        
        # Get daily limit (provider-specific defaults)
        default_limits = {
            "groq": 14400,
            "gemini": 1500,
            "mistral": 10000,
            "huggingface": 5000
        }
        daily_limit = int(
            self.get(
                f"{provider_upper}_KEY_{i}_DAILY_LIMIT",
                str(default_limits.get(provider.lower(), 10000))
            )
        )
        
        keys.append({
            "id": i,
            "key": key_value,
            "priority": priority,
            "daily_limit": daily_limit
        })
        
        i += 1
    
    # Fallback: check for old-style single key (backward compatibility)
    if not keys:
        single_key = self.get(f"{provider_upper}_API_KEY")
        if single_key:
            default_limits = {
                "groq": 14400,
                "gemini": 1500,
                "mistral": 10000
            }
            keys.append({
                "id": 1,
                "key": single_key,
                "priority": 1,
                "daily_limit": default_limits.get(provider.lower(), 10000)
            })
    
    # Sort by priority (lower number = higher priority)
    keys.sort(key=lambda k: k["priority"])
    
    return keys
```

#### 1.2 Testing

```python
# test_secrets_manager.py
def test_get_provider_keys_multiple():
    """Test multiple keys for a provider"""
    # Setup
    secrets = SecretsManager()
    secrets.set("GROQ_API_KEY_1", "sk-1")
    secrets.set("GROQ_KEY_1_PRIORITY", "1")
    secrets.set("GROQ_KEY_1_DAILY_LIMIT", "14400")
    
    secrets.set("GROQ_API_KEY_2", "sk-2")
    secrets.set("GROQ_KEY_2_PRIORITY", "2")
    secrets.set("GROQ_KEY_2_DAILY_LIMIT", "14400")
    
    # Execute
    keys = secrets.get_provider_keys("groq")
    
    # Assert
    assert len(keys) == 2
    assert keys[0]["id"] == 1
    assert keys[0]["priority"] == 1
    assert keys[1]["id"] == 2
    assert keys[1]["priority"] == 2

def test_get_provider_keys_backward_compatible():
    """Test backward compatibility with old single-key format"""
    secrets = SecretsManager()
    secrets.set("GROQ_API_KEY", "sk-old")
    
    keys = secrets.get_provider_keys("groq")
    
    assert len(keys) == 1
    assert keys[0]["key"] == "sk-old"
    assert keys[0]["id"] == 1
```

---

### Task 2: تعديل ModelRouter (1-2 يوم)

**الملف**: `ServerAutomationAI/dev_platform/core/model_router.py`

#### 2.1 تعديل `_check_available_models()`

```python
def _check_available_models(self) -> List[Dict]:
    """
    Check which models have valid API keys with test pings
    
    Returns:
        List of available model configs WITH key info:
        [
            {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 8000,
                "speed": "fastest",
                "key_id": 1,
                "key": "sk-xxx...",
                "priority": 1,
                "daily_limit": 14400
            }
        ]
    """
    available = []
    
    for model_config in self.model_priority:
        provider = model_config["provider"]
        
        # Get all keys for this provider
        provider_keys = self.secrets.get_provider_keys(provider)
        
        if not provider_keys:
            logger.warning(f"No API keys found for {provider}")
            continue
        
        # Test each key
        for key_info in provider_keys:
            # Create extended config with key info
            extended_config = {
                **model_config,
                "key_id": key_info["id"],
                "key": key_info["key"],
                "priority": key_info["priority"],
                "daily_limit": key_info["daily_limit"]
            }
            
            # Validate with test ping
            if self._test_ping_with_key(extended_config):
                available.append(extended_config)
                logger.info(
                    f"✓ {provider} Key {key_info['id']} "
                    f"(Priority {key_info['priority']}) is available"
                )
            else:
                logger.warning(
                    f"✗ {provider} Key {key_info['id']} validation failed"
                )
    
    logger.info(
        f"Available models: "
        f"{[(m['provider'], m['key_id']) for m in available]}"
    )
    return available
```

#### 2.2 إضافة `_test_ping_with_key()`

```python
def _test_ping_with_key(self, model_config: Dict) -> bool:
    """
    Test model availability with specific key
    
    Args:
        model_config: Must include 'key' field
    """
    provider = model_config["provider"]
    key_id = model_config["key_id"]
    api_key = model_config["key"]
    
    # Check cached validation
    cache_key = f"ping_validation_{provider}_key{key_id}"
    cached = self.cache.cache_get(cache_key)
    if cached is not None:
        return cached
    
    if not api_key:
        logger.warning(f"{provider} Key {key_id} is empty")
        self.cache.cache_set(cache_key, False, expire=300)
        return False
    
    try:
        # Minimal test completion
        test_messages = [{"role": "user", "content": "hi"}]
        
        model_name = model_config["model"]
        # Add provider prefix
        if provider == "gemini":
            model_name = f"gemini/{model_name}"
        elif provider == "groq":
            model_name = f"groq/{model_name}"
        elif provider == "mistral":
            model_name = f"mistral/{model_name}"
        
        response = completion(
            model=model_name,
            messages=test_messages,
            max_tokens=3,
            api_key=api_key,
            timeout=5
        )
        
        # Success!
        self.cache.cache_set(cache_key, True, expire=3600)  # 1 hour
        logger.info(
            f"{provider} Key {key_id} credentials validated successfully"
        )
        return True
    
    except AuthenticationError as e:
        logger.error(
            f"{provider} Key {key_id} authentication failed - "
            f"invalid or expired"
        )
        self.cache.cache_set(cache_key, False, expire=300)
        self._save_health_score(f"{provider}_key{key_id}", 0)
        return False
    
    except Timeout:
        logger.warning(f"{provider} Key {key_id} ping timeout")
        return False
    
    except Exception as e:
        logger.warning(
            f"{provider} Key {key_id} ping failed: "
            f"{type(e).__name__} - {str(e)}"
        )
        return False
```

#### 2.3 تعديل `chat()` للاختيار الذكي

```python
def chat(
    self,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    use_cache: bool = True,
    retry_count: int = 3
) -> Dict[str, Any]:
    """Send chat completion request with automatic failover"""
    
    if not self.available_models:
        return self._graceful_downgrade(messages, "no_models_configured")
    
    # Periodically revalidate providers
    if random.random() < 0.1:
        self._revalidate_providers()
    
    # Check cache
    if use_cache:
        cache_key = self._generate_cache_key(messages, temperature)
        cached = self.cache.cache_get(cache_key)
        if cached:
            logger.info("Cache hit for request")
            return cached
    
    # Sort models by:
    # 1. Provider health score
    # 2. Key priority (within same provider)
    sorted_models = sorted(
        self.available_models,
        key=lambda m: (
            -self.health_scores.get(f"{m['provider']}_key{m['key_id']}", 100),
            m['priority']  # Lower priority number = higher priority
        )
    )
    
    # Try each model in sorted order
    last_error = None
    errors_by_provider = {}
    
    for model_config in sorted_models:
        provider = model_config["provider"]
        key_id = model_config["key_id"]
        health_key = f"{provider}_key{key_id}"
        health_score = self.health_scores.get(health_key, 100)
        
        # Skip very unhealthy keys (unless recovery probe)
        if health_score < 20:
            if random.random() < 0.2:  # 20% chance recovery
                logger.info(
                    f"Attempting recovery probe for {provider} "
                    f"Key {key_id} (health: {health_score})"
                )
                if self._probe_unhealthy_key(model_config):
                    logger.info(f"{provider} Key {key_id} recovered!")
                else:
                    logger.warning(f"{provider} Key {key_id} recovery failed")
                    continue
            else:
                logger.debug(
                    f"Skipping {provider} Key {key_id} "
                    f"due to low health: {health_score}"
                )
                continue
        
        # Try this key with retries
        for attempt in range(retry_count):
            try:
                result = self._call_model_with_key(
                    model_config,
                    messages,
                    temperature,
                    max_tokens or model_config["max_tokens"]
                )
                
                # Success!
                self._update_health_score(health_key, success=True)
                
                # Cache successful response
                if use_cache and result.get("content"):
                    cache_key = self._generate_cache_key(messages, temperature)
                    self.cache.cache_set(cache_key, result, expire=3600)
                
                return result
            
            except RateLimitError as e:
                logger.warning(
                    f"{provider} Key {key_id} rate limit hit, "
                    f"trying next key..."
                )
                last_error = self._map_provider_exception(
                    f"{provider}_key{key_id}", e
                )
                errors_by_provider[f"{provider}_key{key_id}"] = last_error
                self._update_health_score(health_key, success=False)
                break  # Skip to next key
            
            except AuthenticationError as e:
                logger.error(
                    f"{provider} Key {key_id} authentication failed - "
                    f"quarantining for 5 minutes"
                )
                last_error = self._map_provider_exception(
                    f"{provider}_key{key_id}", e
                )
                errors_by_provider[f"{provider}_key{key_id}"] = last_error
                
                # Quarantine this specific key
                self._quarantine_key(provider, key_id, model_config)
                break
            
            except (APIError, Timeout) as e:
                logger.warning(
                    f"{provider} Key {key_id} error "
                    f"(attempt {attempt+1}/{retry_count}): {e}"
                )
                last_error = self._map_provider_exception(
                    f"{provider}_key{key_id}", e
                )
                errors_by_provider[f"{provider}_key{key_id}"] = last_error
                
                if attempt < retry_count - 1:
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    logger.debug(
                        f"Retrying {provider} Key {key_id} "
                        f"after {backoff:.2f}s..."
                    )
                    time.sleep(backoff)
                else:
                    self._update_health_score(health_key, success=False)
                continue
            
            except Exception as e:
                logger.error(
                    f"{provider} Key {key_id} unexpected error: {e}"
                )
                last_error = self._map_provider_exception(
                    f"{provider}_key{key_id}", e
                )
                errors_by_provider[f"{provider}_key{key_id}"] = last_error
                self._update_health_score(health_key, success=False)
                break
    
    # All keys failed
    return self._graceful_downgrade(messages, last_error, errors_by_provider)
```

#### 2.4 إضافة `_quarantine_key()`

```python
def _quarantine_key(self, provider: str, key_id: int, model_config: Dict):
    """Quarantine a specific key due to authentication failure"""
    
    # Remove from available models
    self.available_models = [
        m for m in self.available_models
        if not (m["provider"] == provider and m["key_id"] == key_id)
    ]
    
    # Set health to 0
    health_key = f"{provider}_key{key_id}"
    self._save_health_score(health_key, 0)
    
    # Cache validation failure
    cache_key = f"ping_validation_{provider}_key{key_id}"
    self.cache.cache_set(cache_key, False, expire=300)  # 5 min
    
    logger.warning(
        f"{provider} Key {key_id} quarantined for 5 minutes "
        f"due to authentication failure"
    )
```

---

### Task 3: Documentation & Examples (0.5 يوم)

#### 3.1 إنشاء `.env.example`

```bash
# .env.example

# ============================================
# Groq API Keys (3 مفاتيح)
# ============================================
GROQ_API_KEY_1=sk-proj-AAA...
GROQ_KEY_1_PRIORITY=1
GROQ_KEY_1_DAILY_LIMIT=14400

GROQ_API_KEY_2=sk-proj-BBB...
GROQ_KEY_2_PRIORITY=2
GROQ_KEY_2_DAILY_LIMIT=14400

GROQ_API_KEY_3=sk-proj-CCC...
GROQ_KEY_3_PRIORITY=3
GROQ_KEY_3_DAILY_LIMIT=14400

# ============================================
# Gemini API Keys (2 مفاتيح)
# ============================================
GEMINI_API_KEY_1=AIza...XXX
GEMINI_KEY_1_PRIORITY=1
GEMINI_KEY_1_DAILY_LIMIT=1500

GEMINI_API_KEY_2=AIza...YYY
GEMINI_KEY_2_PRIORITY=2
GEMINI_KEY_2_DAILY_LIMIT=1500

# ============================================
# Mistral API Keys (1 مفتاح)
# ============================================
MISTRAL_API_KEY_1=msk...
MISTRAL_KEY_1_PRIORITY=1
MISTRAL_KEY_1_DAILY_LIMIT=10000

# ============================================
# Backward Compatibility (old format still works!)
# ============================================
# GROQ_API_KEY=sk-xxx  # سيُعامل كـ _API_KEY_1
```

#### 3.2 تحديث README.md

```markdown
## Multi-Key Configuration

### Why Multiple Keys?

- **No Service Interruption**: When one key hits its daily limit, automatically switch to backup
- **Load Distribution**: Distribute requests across multiple keys
- **Cost Optimization**: Use free-tier keys efficiently
- **High Availability**: Redundancy for critical workloads

### Setup

1. **Get Multiple API Keys**:
   - Groq: https://console.groq.com/keys (free tier: 14,400 tokens/day per key)
   - Gemini: https://aistudio.google.com/app/apikey (free tier: 1,500 requests/day)

2. **Configure .env**:
   ```bash
   # Copy example
   cp .env.example .env
   
   # Edit with your keys
   nano .env
   ```

3. **Priority System**:
   - Lower number = higher priority
   - System tries keys in priority order
   - Best practice: `1` = primary, `2` = backup, `3` = emergency

### Example Scenarios

**Scenario 1: High-Volume Day**
```
Morning (8 AM):
  Groq Key 1: 0 tokens used → Active
  
Afternoon (2 PM):
  Groq Key 1: 14,400 tokens used (100%) → Exhausted
  Groq Key 2: 0 tokens used → Now Active ✅
  
Evening (6 PM):
  Groq Key 2: 8,000 tokens used → Still Active
  
Midnight (12 AM):
  All keys reset → Ready for tomorrow
```

**Scenario 2: Key Authentication Failure**
```
Request #123:
  Try: Groq Key 1 → AuthenticationError (key expired)
  Quarantine: Groq Key 1 for 5 minutes
  Fallback: Groq Key 2 → Success ✅
```
```

---

## 🧪 Testing Checklist

### ✅ Unit Tests

- [ ] `test_get_provider_keys_multiple()` - Multiple keys
- [ ] `test_get_provider_keys_backward_compatible()` - Single key
- [ ] `test_get_provider_keys_empty()` - No keys
- [ ] `test_get_provider_keys_sorting_by_priority()` - Priority order
- [ ] `test_ping_with_multiple_keys()` - All keys validated
- [ ] `test_ping_with_one_invalid_key()` - Skip invalid, use valid
- [ ] `test_quarantine_specific_key()` - Only quarantine failed key
- [ ] `test_auto_switch_on_rate_limit()` - Switch to next key
- [ ] `test_health_score_per_key()` - Independent health tracking

### ✅ Integration Tests

- [ ] Real API calls with 3 Groq keys
- [ ] Simulate rate limit on Key 1 → verify switch to Key 2
- [ ] Simulate auth error on Key 1 → verify quarantine + switch
- [ ] All keys exhausted → verify graceful degradation
- [ ] Backward compatibility: old `.env` format still works

### ✅ Manual Testing

```bash
# 1. Setup .env with 3 keys
cat > .env << EOF
GROQ_API_KEY_1=sk-valid-key-1
GROQ_API_KEY_2=sk-valid-key-2
GROQ_API_KEY_3=sk-invalid-key
EOF

# 2. Run test script
python -c "
from dev_platform.core.model_router import ModelRouter

router = ModelRouter()
print('Available models:', len(router.available_models))

# Should show 2 valid keys for Groq
for model in router.available_models:
    if model['provider'] == 'groq':
        print(f\"  Groq Key {model['key_id']}: Priority {model['priority']}\")

# Test actual request
response = router.chat([
    {'role': 'user', 'content': 'Hi'}
])
print(f\"Used: {response['model']}\")
"

# 3. Expected output:
# Available models: 2
#   Groq Key 1: Priority 1
#   Groq Key 2: Priority 2
# Used: groq/llama-3.3-70b-versatile (key_1)
```

---

## 📦 Deliverables

1. ✅ Modified `secrets_manager.py` with `get_provider_keys()`
2. ✅ Modified `model_router.py` with multi-key support
3. ✅ All unit tests passing
4. ✅ Integration tests passing
5. ✅ `.env.example` with examples
6. ✅ Updated README.md with documentation
7. ✅ Manual testing completed

---

## 🚀 Handoff to Next Developer

بعد إكمال هذه المهمة، سلّم إلى **Developer AI-Keys-02** لتطبيق:
- **Quota Tracking System** - تتبع الاستهلاك اليومي لكل مفتاح
- **Smart Key Selection** - اختيار بناءً على الحد المتبقي

---

**آخر تحديث**: 2025-11-18  
**الحالة**: 🟡 جاهز للتنفيذ

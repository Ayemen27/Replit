# 🎯 تصميم Model Pool Manager - دليل التنفيذ الكامل

**الهدف:** نظام مركزي لإدارة نماذج AI متعددة (مجانية ومدفوعة) مع failover ذكي وإدارة تكاليف

---

## 📐 البنية المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│                   MODEL POOL MANAGER                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Registry   │  │   Router     │  │   Monitor    │     │
│  │   (Models)   │  │  (Selection) │  │  (Health)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                   │                  │           │
│         └───────────────────┴──────────────────┘           │
│                           │                                │
│  ┌──────────────┬─────────┴─────────┬──────────────┐      │
│  │ Key Manager  │ Usage Tracker     │ Cost Manager │      │
│  └──────────────┴───────────────────┴──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
    ┌───────▼──┐  ┌─────▼────┐  ┌───▼────────┐
    │  Free    │  │  Paid    │  │  Fallback  │
    │  Models  │  │  Models  │  │  (Cache)   │
    └──────────┘  └──────────┘  └────────────┘
```

---

## 🗂️ هيكل الملفات

```
model_pool/
├── __init__.py
├── manager.py              # ModelPoolManager الرئيسي
├── models.py               # Model classes & configurations
├── key_manager.py          # إدارة API Keys
├── usage_tracker.py        # تتبع الاستخدام والتكاليف
├── router.py               # Model selection logic
├── monitor.py              # Health monitoring
├── cost_manager.py         # Cost optimization
├── providers/
│   ├── __init__.py
│   ├── base.py            # BaseProvider interface
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── google_provider.py
│   ├── groq_provider.py
│   ├── cohere_provider.py
│   └── mistral_provider.py
└── utils/
    ├── __init__.py
    ├── encryption.py      # Key encryption
    ├── cache.py           # Response caching
    └── retry.py           # Retry logic
```

---

## 📝 التنفيذ التفصيلي

### 1. Model Configuration (models.py)

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ModelTier(Enum):
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"

class ModelCapability(Enum):
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    ANALYSIS = "analysis"
    FAST = "fast"
    LARGE_CONTEXT = "large_context"

@dataclass
class ModelConfig:
    """تكوين نموذج AI"""
    
    model_id: str
    provider: str
    model_name: str
    tier: ModelTier
    
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    
    rpm_limit: int = 60
    tpm_limit: int = 100000
    context_window: int = 128000
    
    capabilities: List[ModelCapability] = None
    
    max_output_tokens: int = 4096
    temperature_default: float = 0.7
    
    is_active: bool = True
    is_experimental: bool = False
    
    priority: int = 5
    
    metadata: dict = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ModelResponse:
    """استجابة من نموذج"""
    
    model_id: str
    provider: str
    
    content: str
    
    tokens_used: int
    input_tokens: int
    output_tokens: int
    
    cost: float
    response_time_ms: int
    
    success: bool
    error_message: Optional[str] = None
    
    cached: bool = False
    
    metadata: dict = None
```

### 2. Base Provider (providers/base.py)

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseProvider(ABC):
    """
    واجهة موحدة لجميع مزودي النماذج
    """
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ModelResponse:
        """
        إرسال طلب للنموذج
        
        Args:
            prompt: النص المُدخل
            model: اسم النموذج
            temperature: درجة الإبداع
            max_tokens: الحد الأقصى للـ tokens
            **kwargs: معاملات إضافية
            
        Returns:
            ModelResponse
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """اختبار الاتصال بالـ API"""
        pass
    
    @abstractmethod
    def get_usage_info(self) -> Dict[str, Any]:
        """الحصول على معلومات الاستخدام"""
        pass
    
    def calculate_cost(
        self,
        model_config: ModelConfig,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """حساب تكلفة الطلب"""
        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output_tokens
        return input_cost + output_cost
```

### 3. OpenAI Provider (providers/openai_provider.py)

```python
import openai
from typing import Dict, Any
import time
from .base import BaseProvider, ModelResponse

class OpenAIProvider(BaseProvider):
    """مزود OpenAI (GPT-4, GPT-3.5)"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ModelResponse:
        """إرسال طلب لـ OpenAI"""
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            usage = response.usage
            content = response.choices[0].message.content
            
            return ModelResponse(
                model_id=f"openai_{model}",
                provider="openai",
                content=content,
                tokens_used=usage.total_tokens,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost=0.0,  # Will be calculated by manager
                response_time_ms=response_time_ms,
                success=True
            )
            
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return ModelResponse(
                model_id=f"openai_{model}",
                provider="openai",
                content="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                response_time_ms=response_time_ms,
                success=False,
                error_message=str(e)
            )
    
    async def test_connection(self) -> bool:
        """اختبار الاتصال"""
        try:
            await self.client.models.list()
            return True
        except:
            return False
    
    def get_usage_info(self) -> Dict[str, Any]:
        """معلومات الاستخدام (OpenAI لا يوفر API لهذا)"""
        return {"provider": "openai", "note": "No usage API available"}
```

### 4. Groq Provider (مجاني)

```python
from groq import AsyncGroq
from .base import BaseProvider, ModelResponse
import time

class GroqProvider(BaseProvider):
    """مزود Groq (مجاني - Llama 3.3 70B)"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.client = AsyncGroq(api_key=api_key)
    
    async def complete(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ModelResponse:
        """إرسال طلب لـ Groq"""
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            usage = response.usage
            content = response.choices[0].message.content
            
            return ModelResponse(
                model_id=f"groq_{model}",
                provider="groq",
                content=content,
                tokens_used=usage.total_tokens,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost=0.0,  # Free!
                response_time_ms=response_time_ms,
                success=True
            )
            
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return ModelResponse(
                model_id=f"groq_{model}",
                provider="groq",
                content="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                response_time_ms=response_time_ms,
                success=False,
                error_message=str(e)
            )
    
    async def test_connection(self) -> bool:
        """اختبار الاتصال"""
        try:
            await self.complete("test", max_tokens=10)
            return True
        except:
            return False
    
    def get_usage_info(self) -> Dict[str, Any]:
        """معلومات الاستخدام"""
        return {
            "provider": "groq",
            "tier": "free",
            "rpm_limit": 30,
            "tpm_limit": 15000
        }
```

### 5. Model Pool Manager (manager.py)

```python
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import yaml
from pathlib import Path

from .models import ModelConfig, ModelResponse, ModelTier
from .key_manager import APIKeyManager
from .usage_tracker import UsageTracker
from .router import ModelRouter
from .cost_manager import CostManager
from .providers import *

class ModelPoolManager:
    """
    المدير المركزي لجميع نماذج AI
    
    Features:
    - تسجيل نماذج متعددة
    - اختيار ذكي للنموذج
    - Failover تلقائي
    - تتبع التكاليف
    - إدارة API Keys
    """
    
    def __init__(self, config_path: str = "configs/models.yaml"):
        self.config_path = Path(config_path)
        self.models: Dict[str, ModelConfig] = {}
        self.providers: Dict[str, BaseProvider] = {}
        
        self.key_manager = APIKeyManager()
        self.usage_tracker = UsageTracker()
        self.router = ModelRouter(self)
        self.cost_manager = CostManager(self)
        
        self._load_config()
        self._initialize_providers()
        
    def _load_config(self):
        """تحميل تكوينات النماذج"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        for tier_name, models_list in config.get('models', {}).items():
            tier = ModelTier(tier_name.replace('_tier', ''))
            
            for model_conf in models_list:
                model = ModelConfig(
                    model_id=model_conf['id'],
                    provider=model_conf['provider'],
                    model_name=model_conf['model'],
                    tier=tier,
                    cost_per_1k_input_tokens=model_conf.get('cost_per_1k_tokens', 0.0),
                    cost_per_1k_output_tokens=model_conf.get('cost_per_1k_tokens', 0.0),
                    rpm_limit=model_conf.get('rpm_limit', 60),
                    tpm_limit=model_conf.get('tpm_limit', 100000),
                    capabilities=[c for c in model_conf.get('capabilities', [])]
                )
                
                self.models[model.model_id] = model
    
    def _initialize_providers(self):
        """تهيئة مزودي النماذج"""
        
        provider_classes = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'google': GoogleProvider,
            'groq': GroqProvider,
            'cohere': CohereProvider,
            'mistral': MistralProvider
        }
        
        for provider_name, provider_class in provider_classes.items():
            try:
                api_key = self.key_manager.get_key(provider_name)
                if api_key:
                    self.providers[provider_name] = provider_class(api_key)
            except Exception as e:
                print(f"Warning: Could not initialize {provider_name}: {e}")
    
    async def execute_task(
        self,
        prompt: str,
        task_type: str = "general",
        priority: str = "normal",
        preferred_tier: Optional[ModelTier] = None,
        **kwargs
    ) -> ModelResponse:
        """
        تنفيذ مهمة مع اختيار تلقائي للنموذج المناسب
        
        Args:
            prompt: المُدخل
            task_type: نوع المهمة (reasoning, coding, analysis, etc.)
            priority: الأولوية (low, normal, high, critical)
            preferred_tier: الطبقة المُفضلة (free, paid, premium)
            
        Returns:
            ModelResponse
        """
        
        # 1. اختيار النموذج المناسب
        selected_model = await self.router.select_model(
            task_type=task_type,
            priority=priority,
            preferred_tier=preferred_tier
        )
        
        if not selected_model:
            return ModelResponse(
                model_id="none",
                provider="none",
                content="",
                tokens_used=0,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                response_time_ms=0,
                success=False,
                error_message="No available model found"
            )
        
        # 2. محاولة التنفيذ مع fallback
        return await self._execute_with_fallback(selected_model, prompt, **kwargs)
    
    async def _execute_with_fallback(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> ModelResponse:
        """
        تنفيذ مع إعادة المحاولة والـ fallback
        """
        
        models_to_try = [model_config]
        
        # إضافة نماذج بديلة
        fallback_models = self.router.get_fallback_models(model_config)
        models_to_try.extend(fallback_models[:2])
        
        last_error = None
        
        for model in models_to_try:
            provider = self.providers.get(model.provider)
            
            if not provider:
                continue
            
            for retry in range(max_retries):
                try:
                    response = await provider.complete(
                        prompt=prompt,
                        model=model.model_name,
                        **kwargs
                    )
                    
                    if response.success:
                        # حساب التكلفة
                        response.cost = provider.calculate_cost(
                            model,
                            response.input_tokens,
                            response.output_tokens
                        )
                        
                        # تسجيل الاستخدام
                        await self.usage_tracker.track_request(
                            model_id=model.model_id,
                            tokens=response.tokens_used,
                            cost=response.cost,
                            success=True
                        )
                        
                        return response
                        
                except Exception as e:
                    last_error = e
                    await asyncio.sleep(1 * (retry + 1))
                    continue
        
        # جميع المحاولات فشلت
        return ModelResponse(
            model_id=model_config.model_id,
            provider=model_config.provider,
            content="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            response_time_ms=0,
            success=False,
            error_message=f"All models failed. Last error: {last_error}"
        )
    
    async def get_model_status(self, model_id: str) -> Dict:
        """حالة نموذج معين"""
        model = self.models.get(model_id)
        
        if not model:
            return {"error": "Model not found"}
        
        provider = self.providers.get(model.provider)
        
        usage = await self.usage_tracker.get_model_usage(model_id)
        
        return {
            "model_id": model_id,
            "provider": model.provider,
            "tier": model.tier.value,
            "is_active": model.is_active,
            "usage_today": usage,
            "health": "ok" if provider else "no_provider"
        }
    
    async def get_system_status(self) -> Dict:
        """حالة النظام الكاملة"""
        
        total_models = len(self.models)
        active_models = len([m for m in self.models.values() if m.is_active])
        
        daily_usage = await self.usage_tracker.get_daily_usage()
        daily_cost = await self.cost_manager.get_daily_cost()
        
        return {
            "total_models": total_models,
            "active_models": active_models,
            "providers": list(self.providers.keys()),
            "daily_requests": daily_usage.get('total_requests', 0),
            "daily_tokens": daily_usage.get('total_tokens', 0),
            "daily_cost": daily_cost,
            "cost_budget": self.cost_manager.daily_budget,
            "cost_remaining": max(0, self.cost_manager.daily_budget - daily_cost)
        }
```

### 6. Model Router (router.py)

```python
from typing import Optional, List
from .models import ModelConfig, ModelTier, ModelCapability

class ModelRouter:
    """
    محرك اختيار النماذج الذكي
    """
    
    def __init__(self, pool_manager):
        self.pool = pool_manager
        
    async def select_model(
        self,
        task_type: str = "general",
        priority: str = "normal",
        preferred_tier: Optional[ModelTier] = None
    ) -> Optional[ModelConfig]:
        """
        اختيار أفضل نموذج للمهمة
        
        Logic:
        1. فلترة النماذج المناسبة حسب task_type
        2. ترتيب حسب الأولوية والتكلفة
        3. فحص الـ quota المتبقية
        4. اختيار الأفضل
        """
        
        # 1. النماذج النشطة فقط
        available_models = [
            m for m in self.pool.models.values()
            if m.is_active
        ]
        
        # 2. فلترة حسب الطبقة المفضلة
        if preferred_tier:
            available_models = [
                m for m in available_models
                if m.tier == preferred_tier
            ]
        
        # 3. فلترة حسب القدرات المطلوبة
        required_capability = self._map_task_to_capability(task_type)
        
        if required_capability:
            available_models = [
                m for m in available_models
                if required_capability in m.capabilities
            ]
        
        # 4. فحص الـ quota
        models_with_quota = []
        for model in available_models:
            has_quota = await self._check_quota(model)
            if has_quota:
                models_with_quota.append(model)
        
        if not models_with_quota:
            return None
        
        # 5. ترتيب وإرجاع الأفضل
        sorted_models = self._sort_models(models_with_quota, priority)
        
        return sorted_models[0] if sorted_models else None
    
    def _map_task_to_capability(self, task_type: str) -> Optional[ModelCapability]:
        """تحويل نوع المهمة إلى قدرة مطلوبة"""
        
        mapping = {
            "coding": ModelCapability.CODING,
            "analysis": ModelCapability.ANALYSIS,
            "reasoning": ModelCapability.REASONING,
            "vision": ModelCapability.VISION,
            "fast": ModelCapability.FAST
        }
        
        return mapping.get(task_type)
    
    async def _check_quota(self, model: ModelConfig) -> bool:
        """فحص إذا كان النموذج لديه quota متبقية"""
        
        usage = await self.pool.usage_tracker.get_model_usage(model.model_id)
        
        requests_today = usage.get('requests_today', 0)
        tokens_today = usage.get('tokens_today', 0)
        
        rpm_ok = requests_today < model.rpm_limit * 24 * 60
        tpm_ok = tokens_today < model.tpm_limit * 24 * 60
        
        return rpm_ok and tpm_ok
    
    def _sort_models(
        self,
        models: List[ModelConfig],
        priority: str
    ) -> List[ModelConfig]:
        """ترتيب النماذج حسب الأفضلية"""
        
        if priority == "low":
            # المجاني أولاً، ثم الأرخص
            return sorted(
                models,
                key=lambda m: (m.tier.value, m.cost_per_1k_input_tokens)
            )
        elif priority == "critical":
            # الأفضل أولاً، بغض النظر عن التكلفة
            return sorted(
                models,
                key=lambda m: (-m.priority, m.tier.value)
            )
        else:
            # توازن بين الجودة والتكلفة
            return sorted(
                models,
                key=lambda m: (m.tier.value, -m.priority)
            )
    
    def get_fallback_models(
        self,
        model: ModelConfig,
        max_fallbacks: int = 3
    ) -> List[ModelConfig]:
        """الحصول على نماذج بديلة"""
        
        fallbacks = []
        
        for m in self.pool.models.values():
            if m.model_id == model.model_id:
                continue
            
            if m.is_active and m.tier in [ModelTier.FREE, model.tier]:
                fallbacks.append(m)
        
        fallbacks.sort(key=lambda m: (m.tier.value, m.cost_per_1k_input_tokens))
        
        return fallbacks[:max_fallbacks]
```

---

## 🔑 API Key Manager (key_manager.py)

```python
from cryptography.fernet import Fernet
import os
from pathlib import Path
import json

class APIKeyManager:
    """
    إدارة آمنة لـ API Keys
    
    Features:
    - تخزين مُشفر
    - Rotation
    - Access logging
    """
    
    def __init__(self, keys_file: str = ".api_keys.enc"):
        self.keys_file = Path(keys_file)
        self.cipher = self._get_cipher()
        self.keys = self._load_keys()
    
    def _get_cipher(self) -> Fernet:
        """الحصول على مفتاح التشفير"""
        
        key_env = os.getenv("ENCRYPTION_KEY")
        
        if not key_env:
            # إنشاء مفتاح جديد
            key = Fernet.generate_key()
            print(f"⚠️ Set ENCRYPTION_KEY={key.decode()}")
            return Fernet(key)
        
        return Fernet(key_env.encode())
    
    def _load_keys(self) -> dict:
        """تحميل المفاتيح المُشفرة"""
        
        if not self.keys_file.exists():
            return {}
        
        encrypted_data = self.keys_file.read_bytes()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        return json.loads(decrypted_data.decode())
    
    def _save_keys(self):
        """حفظ المفاتيح المُشفرة"""
        
        data = json.dumps(self.keys).encode()
        encrypted_data = self.cipher.encrypt(data)
        
        self.keys_file.write_bytes(encrypted_data)
        
        # صلاحيات القراءة فقط للمالك
        os.chmod(self.keys_file, 0o600)
    
    def store_key(self, provider: str, api_key: str, metadata: dict = None):
        """تخزين مفتاح API"""
        
        self.keys[provider] = {
            "key": api_key,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        self._save_keys()
    
    def get_key(self, provider: str) -> str:
        """استرجاع مفتاح API"""
        
        key_data = self.keys.get(provider)
        
        if not key_data:
            raise KeyError(f"No API key for provider: {provider}")
        
        return key_data["key"]
    
    def delete_key(self, provider: str):
        """حذف مفتاح"""
        
        if provider in self.keys:
            del self.keys[provider]
            self._save_keys()
```

---

## 📊 Usage Tracker (usage_tracker.py)

```python
import asyncpg
from datetime import datetime, date
from typing import Dict

class UsageTracker:
    """
    تتبع استخدام النماذج
    """
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.pool = None
    
    async def initialize(self):
        """تهيئة اتصال قاعدة البيانات"""
        
        self.pool = await asyncpg.create_pool(self.db_url)
    
    async def track_request(
        self,
        model_id: str,
        tokens: int,
        cost: float,
        success: bool,
        task_type: str = None,
        response_time_ms: int = 0,
        error_message: str = None
    ):
        """تسجيل طلب"""
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO usage_logs
                (model_id, task_type, tokens_used, cost, response_time_ms, success, error_message)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, model_id, task_type, tokens, cost, response_time_ms, success, error_message)
            
            # تحديث الملخص اليومي
            await self._update_daily_summary(conn, model_id, tokens, cost, success)
    
    async def _update_daily_summary(
        self,
        conn,
        model_id: str,
        tokens: int,
        cost: float,
        success: bool
    ):
        """تحديث الملخص اليومي"""
        
        today = date.today()
        
        await conn.execute("""
            INSERT INTO daily_usage_summary
            (date, model_id, total_requests, total_tokens, total_cost)
            VALUES ($1, $2, 1, $3, $4)
            ON CONFLICT (date, model_id)
            DO UPDATE SET
                total_requests = daily_usage_summary.total_requests + 1,
                total_tokens = daily_usage_summary.total_tokens + $3,
                total_cost = daily_usage_summary.total_cost + $4
        """, today, model_id, tokens, cost)
    
    async def get_model_usage(self, model_id: str) -> Dict:
        """احصائيات نموذج معين"""
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT
                    total_requests,
                    total_tokens,
                    total_cost,
                    success_rate
                FROM daily_usage_summary
                WHERE date = CURRENT_DATE AND model_id = $1
            """, model_id)
            
            if not row:
                return {
                    "requests_today": 0,
                    "tokens_today": 0,
                    "cost_today": 0.0,
                    "success_rate": 100.0
                }
            
            return {
                "requests_today": row['total_requests'],
                "tokens_today": row['total_tokens'],
                "cost_today": float(row['total_cost']),
                "success_rate": float(row['success_rate']) if row['success_rate'] else 100.0
            }
    
    async def get_daily_usage(self) -> Dict:
        """الاستخدام الإجمالي اليوم"""
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT
                    SUM(total_requests) as total_requests,
                    SUM(total_tokens) as total_tokens,
                    SUM(total_cost) as total_cost
                FROM daily_usage_summary
                WHERE date = CURRENT_DATE
            """)
            
            return {
                "total_requests": row['total_requests'] or 0,
                "total_tokens": row['total_tokens'] or 0,
                "total_cost": float(row['total_cost']) if row['total_cost'] else 0.0
            }
```

---

## 💰 Cost Manager (cost_manager.py)

```python
class CostManager:
    """
    إدارة التكاليف
    """
    
    def __init__(self, pool_manager, daily_budget: float = 10.0):
        self.pool = pool_manager
        self.daily_budget = daily_budget
        self.alert_threshold = 0.8
    
    async def get_daily_cost(self) -> float:
        """التكلفة اليومية"""
        
        usage = await self.pool.usage_tracker.get_daily_usage()
        return usage.get('total_cost', 0.0)
    
    async def check_budget(self) -> Dict:
        """فحص الميزانية"""
        
        daily_cost = await self.get_daily_cost()
        
        remaining = self.daily_budget - daily_cost
        percentage_used = (daily_cost / self.daily_budget) * 100
        
        status = "ok"
        if percentage_used >= 100:
            status = "exceeded"
        elif percentage_used >= self.alert_threshold * 100:
            status = "warning"
        
        return {
            "daily_budget": self.daily_budget,
            "daily_cost": daily_cost,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "status": status
        }
    
    async def get_cost_breakdown(self) -> List[Dict]:
        """توزيع التكاليف حسب النموذج"""
        
        async with self.pool.usage_tracker.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    model_id,
                    total_cost,
                    total_requests
                FROM daily_usage_summary
                WHERE date = CURRENT_DATE
                ORDER BY total_cost DESC
            """)
            
            return [
                {
                    "model_id": row['model_id'],
                    "cost": float(row['total_cost']),
                    "requests": row['total_requests']
                }
                for row in rows
            ]
```

---

## 🧪 مثال الاستخدام

```python
# example_usage.py
import asyncio
from model_pool import ModelPoolManager

async def main():
    # 1. تهيئة Model Pool
    pool = ModelPoolManager()
    
    # 2. استخدام بسيط
    response = await pool.execute_task(
        prompt="اكتب دالة Python لحساب Fibonacci",
        task_type="coding",
        priority="normal"
    )
    
    print(f"Model: {response.model_id}")
    print(f"Cost: ${response.cost:.4f}")
    print(f"Response: {response.content}")
    
    # 3. حالة النظام
    status = await pool.get_system_status()
    print(f"Daily cost: ${status['daily_cost']:.2f}/{status['cost_budget']:.2f}")
    
    # 4. استخدام نموذج محدد
    response = await pool.execute_task(
        prompt="شرح مفهوم التعلم العميق",
        preferred_tier=ModelTier.FREE  # مجاني فقط
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

**المرحلة التالية:** تنفيذ Dashboard (React + FastAPI)

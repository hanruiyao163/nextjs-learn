function reactive(obj) {
  return new Proxy(obj, {
      get(target, key) {
          track(target, key);
          return target[key];
      },
      set(target, key, value) {
          target[key] = value;
          trigger(target, key);
          return true;
      }
  });
}

function ref(value) {
  const refObject = {
      get value() {
          track(refObject, 'value');
          return value;
      },
      set value(newValue) {
          value = newValue;
          trigger(refObject, 'value');
      }
  };
  return refObject;
}

let activeEffect;

function track(target, key) {
  if (activeEffect) {
      const effects = getSubscribersForProperty(target, key);
      effects.add(activeEffect);
  }
}

function trigger(target, key) {
  const effects = getSubscribersForProperty(target, key);
  effects.forEach(effect => effect());
}

function whenDepsChange(update) {
  const effect = () => {
      activeEffect = effect;
      update();
      activeEffect = null;
  };
  effect();
}

const targetMap = new WeakMap();

function getSubscribersForProperty(target, key) {
  let subscribers = targetMap.get(target);
  if (!subscribers) {
      subscribers = new Map();
      targetMap.set(target, subscribers);
  }
  let effects = subscribers.get(key);
  if (!effects) {
      effects = new Set();
      subscribers.set(key, effects);
  }
  return effects;
}

const watchEffect = whenDepsChange;
const state = reactive({ count: 0 });

whenDepsChange(() => {
  console.log(`Count is: ${state.count}`);
});

state.count = 1;  // 输出: Count is: 1
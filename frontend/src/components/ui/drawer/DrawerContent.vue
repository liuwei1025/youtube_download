<script setup>
import { computed, inject } from "vue";
import { useForwardPropsEmits } from "reka-ui";
import { DrawerContent, DrawerPortal } from "vaul-vue";
import { cn } from '@/shared/lib';
import DrawerOverlay from "./DrawerOverlay.vue";

const props = defineProps({
  forceMount: { type: Boolean, required: false },
  disableOutsidePointerEvents: { type: Boolean, required: false },
  asChild: { type: Boolean, required: false },
  as: { type: null, required: false },
  class: { type: null, required: false },
});
const emits = defineEmits([
  "escapeKeyDown",
  "pointerDownOutside",
  "focusOutside",
  "interactOutside",
  "openAutoFocus",
  "closeAutoFocus",
]);

const forwarded = useForwardPropsEmits(props, emits);

// 获取父组件传递的 direction
const direction = inject('drawerDirection', 'bottom');

const positionClasses = computed(() => {
  if (direction === 'right') {
    return 'fixed inset-y-0 right-0 z-50 flex h-full flex-col border-l bg-background'
  } else if (direction === 'left') {
    return 'fixed inset-y-0 left-0 z-50 flex h-full flex-col border-r bg-background'
  }
  // 默认底部
  return 'fixed inset-x-0 bottom-0 z-50 mt-24 flex h-auto flex-col rounded-t-[10px] border bg-background'
});

const showHandle = computed(() => direction === 'bottom');
</script>

<template>
  <DrawerPortal>
    <DrawerOverlay />
    <DrawerContent
      v-bind="forwarded"
      :class="cn(positionClasses, props.class)"
    >
      <div v-if="showHandle" class="mx-auto mt-4 h-2 w-[100px] rounded-full bg-muted" />
      <slot />
    </DrawerContent>
  </DrawerPortal>
</template>

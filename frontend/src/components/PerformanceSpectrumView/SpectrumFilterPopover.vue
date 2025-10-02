<template>
  <Sheet v-model:open="model">
    <SheetContent class="pl-3">
      <SheetHeader>
        <SheetTitle>Applied filters overview</SheetTitle>
        <SheetDescription>
          <div class="-mx-3">
            <filter-indication :filters="filters" @remove="emit('remove', $event)"></filter-indication>
          </div>
        </SheetDescription>
      </SheetHeader>
    </SheetContent>
  </Sheet>
</template>
<script setup lang="js">

import {Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle} from "@/components/ui/sheet";
import FilterIndication from "@/components/PerformanceSpectrumView/FilterIndication.vue";

const model = defineModel({
  type: Boolean,
  default: false
})


const emit = defineEmits(['remove'])

defineProps({
  filters: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped lang="scss">
</style>
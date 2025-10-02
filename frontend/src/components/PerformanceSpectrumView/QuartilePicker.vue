<template>
  <Popover v-model:open="popoverModel">
    <PopoverTrigger as-child>
      <Button variant="outline" class="w-[180px] justify-start text-left font-normal">
        <ChartColumnIncreasing :class="enabled ? 'text-blue-500' :'text-white'"/>
        <div class="text-gray-500" v-if="!enabled">Select quartile filter</div>
        <div v-else class="text-blue-500">{{value.label}}</div>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[300px]">
      <segment-combobox :options="quartile_options" placeholder="Select quartile filter" v-model="value">
        <template #item="{option}">
          <div>
            <div class="flex items-center gap-2">
              <div :style="{backgroundColor: option.color}" class="w-2 h-2 rounded-full"></div>
              <span class="text-sm text-gray-500">{{option.label}}</span>
            </div>
          </div>
        </template>
      </segment-combobox>
      <Button class="mt-2 w-full" :disabled="!value" @click="applyQuartile">Apply</Button>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="js">

import Button from "@/components/ui/button/Button.vue";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover/index.js";
import {ChartColumnIncreasing} from "lucide-vue-next";
import SegmentCombobox from "@/components/SegmentCombobox.vue";
import {QUARTILE_COLORS} from "@/constants.js";
import {ref} from "vue";

defineProps({
    enabled: {
        type: Boolean,
        default: false
    }
})

const popoverModel = ref(false)
const quartile_options = [
    {key: 0.25, label: 'Filter for Q1', color: QUARTILE_COLORS.BLUE},
    {key: 0.5, label: 'Filter for Q2', color: QUARTILE_COLORS.YELLOW},
    {key: 0.75, label: 'Filter for Q3', color: QUARTILE_COLORS.ORANGE},
    {key: 1, label: 'Filter for Q4', color: QUARTILE_COLORS.RED},
]

const emit = defineEmits(['apply'])


const value = defineModel({required: true})

const applyQuartile = () => {
    popoverModel.value = false
    emit('apply', value)
}
</script>

<style scoped lang="scss">

</style>
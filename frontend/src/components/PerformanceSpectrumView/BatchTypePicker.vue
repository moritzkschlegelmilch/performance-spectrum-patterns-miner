<template>
  <Popover v-model:open="popoverModel">
    <PopoverTrigger as-child>
      <Button variant="outline" class="w-[180px] justify-start text-left font-normal">
        <Merge :class="enabled ? 'text-blue-500' :'text-white'"/>
        <div class="text-gray-500" v-if="!enabled">Select batch type</div>
        <div v-else class="text-blue-500 truncate">{{batchType?.label}}</div>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[300px]">
      <segment-combobox :options="BATCH_TYPES" placeholder="Select batch type" v-model="batchType"></segment-combobox>
      <Separator class="my-3"></Separator>
      <div class="mb-1 text-sm text-gray-500">DBSCAN - Epsilon in minutes</div>
      <NumberField
        class="mt-2"
        id="number"
        v-model="epsilon"
        :default-value="10"
        :step="0.01"
        :format-options="{
          minimumFractionDigits: 2,
        }">
        <NumberFieldContent>
          <NumberFieldDecrement />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>


      <div class="mb-1 mt-2 text-sm text-gray-500">DBSCAN - Min samples</div>
      <NumberField class="mt-2" v-model="minSamples">
        <NumberFieldContent>
          <NumberFieldDecrement />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>
      <Button class="mt-2 w-full" :disabled="inputDisabled" @click="applyFilter">Apply</Button>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="js">

import Button from "@/components/ui/button/Button.vue";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover/index.js";
import {Merge} from "lucide-vue-next";
import SegmentCombobox from "@/components/SegmentCombobox.vue";
import {
    NumberField,
    NumberFieldContent,
    NumberFieldDecrement,
    NumberFieldIncrement,
    NumberFieldInput,
} from '@/components/ui/number-field'
import Separator from "@/components/ui/separator/Separator.vue";
import {computed, ref} from "vue";
import {BATCH_TYPES} from "@/composables/useEventLogState.js";

defineProps({
    enabled: {
        type: Boolean,
        default: false
    }
})
const emit = defineEmits(['apply'])
const batchType = defineModel('batchType', {required: true})
const epsilon = defineModel('epsilon', {required: true})
const minSamples = defineModel('minSamples', {required: true})
const popoverModel = ref(false)

const inputDisabled = computed(() => {
    return !batchType.value || epsilon.value <= 0 || minSamples.value <= 0
})


const applyFilter = () => {
    popoverModel.value = false
    emit('apply')
}
</script>
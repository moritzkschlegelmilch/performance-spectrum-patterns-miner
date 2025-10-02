<template>
  <segment-combobox
    class="w-[180px]"
    placeholder="Select quartile filter"
    :options="segments"
    @update:model-value="update"
    :model-value="segments[value]"
  />
</template>

<script setup lang="js">
import {computed} from "vue";
import SegmentCombobox from "@/components/SegmentCombobox.vue";
import {useEventLogState} from "@/composables/useEventLogState.js";
import {useConfigurationState} from "@/composables/useConfigurationState.js";


const {getVariantSegments} = useConfigurationState()
const props = defineProps({
  variant: {
    type: Array,
    required: true,
  }
})

const value = defineModel({
  type: Number,
  required: true,
})

const segments = computed(() => {
    return getVariantSegments(props.variant)
})

const update = (val) => {
    value.value = val.key
}
</script>

<style scoped lang="scss">

</style>
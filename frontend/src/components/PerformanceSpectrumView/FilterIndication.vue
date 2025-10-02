<template>
  <div
    class="hover:bg-gray-900 cursor-pointer p-3 flex gap-2 items-center"
    :class="{'bg-gray-900': loadingConfiguration}"
    v-for="filter in filters"
    :key="filter.type.id"
    @click="!loadingConfiguration ? emit('remove', filter) : ''"
  >
    <div>
      <div class="text-sm text-blue-500 font-bold">{{filter.type.name}}</div>
      <div class="text-xs text-gray-500">{{filter.type.displayData(filter.data)}}</div>
    </div>
    <X :size="18" class="ml-auto flex-shrink-0" v-if="!loadingConfiguration"></X>
  </div>
</template>

<script setup lang="js">
import {X} from 'lucide-vue-next'
import {useConfigurationState} from "@/composables/useConfigurationState.js";

const {loadingConfiguration} = useConfigurationState()

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
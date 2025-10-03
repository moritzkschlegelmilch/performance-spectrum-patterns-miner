<template>
    <spectrum-filter-popover
      v-model="sidePopoverOpen"
      :filters="currentFiltersForAllSpectra[currentSpectrum] ?? []"
      @remove="removeFilter">
    </spectrum-filter-popover>

    <div class="flex overflow-hidden items-center">
      <ColoringLegend class="mt-3"></ColoringLegend>
      <div class="flex ml-auto flex-shrink-0 items-center gap-2" v-if="inSideBySideView">
        <Info :size="18" class="text-gray-400"/>
        <div class="text-gray-400 max-w-[380px] truncate overflow-hidden text-sm">
          You are currently editing <span class="text-white font-bold">"{{selectedConfiguration.name}}"</span>
        </div>
        <Button variant="text" class="w-[60px] text-blue-500 font-bold text-sm cursor-pointer" @click="switchView">
          Switch
        </Button>
      </div>
    </div>
    <Separator class="mt-3"></Separator>
    <div class="flex items-center gap-2 sticky top-0 z-10 bg-black py-2">
      <div
        v-if="loadingConfiguration"
        class="absolute top-0 left-0 w-full h-full bg-gray-900 opacity-50 rounded-lg z-10">
      </div>
      <div class="ml-2 text-sm font-bold" v-if="!loadingEventLog">Filtering</div>
      <Loader2 class="animate-spin" v-else></Loader2>
      <Undo :size="22" @click="undoFilter" :class="{'text-gray-500': !caseFilterHistory.length}" class="ml-auto"/>

      <DatePicker v-model="dateModel" @apply="setFilterDate(dateModel)"></DatePicker>
      <Card class="p-0">
        <CardContent class="flex items-center gap-2 p-1">
          <filter-spectrum-selection
            v-if="!!variantFilter"
            v-model="currentSpectrum"
            :variant="variantFilter">
          </filter-spectrum-selection>
          <quartile-picker
            v-model="quartilePickerModel"
            @apply="setQuartileFilter(quartilePickerModel)"
            :enabled="!!getFilterOfType(CASE_FILTERS.QUARTILE)">
          </quartile-picker>
          <batch-type-picker
            v-model:batch-type="clusteringModel.batchType"
            v-model:epsilon="clusteringModel.epsilon"
            v-model:min-samples="clusteringModel.minSamples"
            v-model:fifo-only="clusteringModel.fifoOnly"
            :enabled="clusteringModel.enabled"
            @apply="applyClustering"
          />
        </CardContent>
      </Card>
      <side-by-side-configuration-picker></side-by-side-configuration-picker>
      <Popover v-model:open="popoverActive">
        <PopoverTrigger as-child>
          <Button variant="secondary" class="w-[110px]">
            <ListFilterPlus />
            Filters
            <Badge v-if="activeFilterCount">{{activeFilterCount}}</Badge>
          </Button>
        </PopoverTrigger>
        <PopoverContent class="w-[300px]" side="bottom" align="end">
          <div class="text-sm font-bold ml-1">Global filters</div>
          <div class="flex flex-col gap-2 mt-2" v-if="activeGlobalFilters.length">
            <filter-indication
              :filters="activeGlobalFilters"
              @remove="removeFilterFromSpectrum(GLOBAL_CASE_FILTER, $event)">
            </filter-indication>
          </div>
          <div v-else class="text-gray-500 text-sm mt-1 ml-1">No filters selected</div>

          <Separator class="my-3"></Separator>
          <div v-if="individualSpectrumFilters.length" class="pb-3">
            <div class="text-sm ml-1 mb-1 text-gray-500">Individual spectra</div>
            <div
              class="hover:bg-gray-900 cursor-pointer p-3 flex gap-2 items-center"
              v-for="filter in individualSpectrumFilters"
              :key="filter.spectrumIndex"
              @click="openSidePopup(filter.spectrumIndex)"
            >
              <div>
                <div class="text-sm text-blue-500 font-bold">{{filter.spectrum}}</div>
                <div class="text-xs text-gray-500">{{filter.count}} enabled</div>
              </div>
              <ArrowRight :size="18" class="ml-auto"></ArrowRight>
            </div>
          </div>

          <div class="text-sm ml-1 mb-1 text-gray-500">Filter by segment</div>
          <segment-combobox
            v-model="segmentModel.start"
            :options="activityOptions"
            show-search-bar>
          </segment-combobox>
          <segment-combobox
            class="mt-2"
            v-model="segmentModel.end"
            :options="activityOptions"
            show-search-bar
          ></segment-combobox>
          <Button
            variant="secondary"
            class="w-full mt-2"
            :disabled="segmentModel.start === segmentModel.end || !segmentModel.start || !segmentModel.end"
            @click="segmentFilterActivated"
          >
            Filter segment
          </Button>
        </PopoverContent>
      </Popover>
      <Button @click="exportEventLog(currentEventLog?.event_log.id)" :disabled="loadingConfiguration">
        Export
        <Download v-if="!exportingLog"/>
        <Loader2 class="animate-spin" v-else/>
      </Button>
    </div>
</template>

<script setup lang="js">

import Button from "@/components/ui/button/Button.vue";
import {ListFilterPlus, Undo, ArrowRight, Loader2, Download, Info} from 'lucide-vue-next';
import Badge from "@/components/ui/badge/Badge.vue";
import {useEventLogState} from "@/composables/useEventLogState.js";
import DatePicker from "@/components/DatePicker.vue";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover'
import SegmentCombobox from "@/components/SegmentCombobox.vue";
import Separator from "@/components/ui/separator/Separator.vue";
import {computed, ref} from "vue";
import ColoringLegend from "@/components/PerformanceSpectrumView/ColoringLegend.vue";
import BatchTypePicker from "@/components/PerformanceSpectrumView/BatchTypePicker.vue";
import QuartilePicker from "@/components/PerformanceSpectrumView/QuartilePicker.vue";
import {sum} from "lodash";
import FilterSpectrumSelection from "@/components/PerformanceSpectrumView/FilterSpectrumSelection.vue";
import {GLOBAL_CASE_FILTER} from "@/constants.js";
import CardContent from "@/components/ui/card/CardContent.vue";
import Card from "@/components/ui/card/Card.vue";
import FilterIndication from "@/components/PerformanceSpectrumView/FilterIndication.vue";
import SpectrumFilterPopover from "@/components/PerformanceSpectrumView/SpectrumFilterPopover.vue";
import {useConfigurationState} from "@/composables/useConfigurationState.js";
import SideBySideConfigurationPicker from "@/components/PerformanceSpectrumView/SideBySideConfigurationPicker.vue";
import {CASE_FILTERS} from "@/caseFilters.js";

const props = defineProps({
    configurationId: {
        type: String,
        required: true
    }
})

const {
    configuration,
    loadingConfiguration,
    caseFilterHistory,
    dateModel,
    segmentModel,
    clusteringModel,
    quartilePickerModel,
    currentSpectrum,
    currentFiltersForAllSpectra,
    loadingEventLog,
    exportingLog,
    exportEventLog,
    setQuartileFilter,
    setClusteringFilter,
    setFilterDate,
    setSegmentFilter,
    undoFilter,
    getFilterOfTypeForSpectrum,
    removeFilterFromSpectrum,
} = useConfigurationState(props.configurationId)

const {
    selectedConfiguration,
    inSideBySideView,
    switchView
} = useEventLogState()

const sidePopoverOpen = ref(false)
const popoverActive = ref(false)

const getFilterOfType = computed(() => getFilterOfTypeForSpectrum(currentSpectrum.value))
const getGlobalFilterOfType = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)

const segmentFilterActivated = () => {
    setSegmentFilter(segmentModel.value.start, segmentModel.value.end)
    popoverActive.value = false
}

const openSidePopup = (spectrum) => {
    currentSpectrum.value = spectrum
    sidePopoverOpen.value = true
}


const removeFilter = (filter) => {
    removeFilterFromSpectrum(currentSpectrum.value, filter)
    sidePopoverOpen.value = false
}


const applyClustering = () => {
    setClusteringFilter(
        clusteringModel.value.batchType,
        clusteringModel.value.epsilon,
        clusteringModel.value.minSamples,
        clusteringModel.value.fifoOnly
    )
}


const variantFilter = computed(() => {
    return getGlobalFilterOfType(CASE_FILTERS.VARIANT)
})

const individualSpectrumFilters = computed(() => {
    return Object.entries(currentFiltersForAllSpectra.value).filter(
        ([key, value]) => key !== GLOBAL_CASE_FILTER && value?.length > 0
    ).map(
        ([spectrumIndex, value]) => {
            const spectrum = variantFilter.value ?
                `${variantFilter.value[+spectrumIndex]} -> ${variantFilter.value[+spectrumIndex + 1]}`
                : 'Entire spectrum'
            return {
                spectrum,
                spectrumIndex,
                count: value.length
            }
        }
    )
})

// Count of active filters across all spectra and global filters
const activeFilterCount = computed(() => {
    return sum(Object.values(currentFiltersForAllSpectra.value).map(f => f.length))
})

// Array of global filters
const activeGlobalFilters = computed(() => {
    return currentFiltersForAllSpectra.value[GLOBAL_CASE_FILTER] ?? []
})


// List of segments in the current variant, formatted like [{label: ..., key: ...}, ...]
const activityOptions = computed(() => {
    return Object.values(configuration.value.spectra?.[0].statistics.activities).map(activity => ({
        label: activity,
        key: activity
    }))
})


</script>
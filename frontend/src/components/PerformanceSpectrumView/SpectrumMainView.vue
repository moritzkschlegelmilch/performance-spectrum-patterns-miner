<template>
  <div>
    <Card class="p-0">
      <!-- actual performance spectrum view -->
      <CardContent class="p-0">
        <SpectrumSelectionWrapper @selected="selectRelativeTimeSpan">
            <performance-spectrum
              v-for="(spectrum, index) in configuration?.spectra"
              :key="index"
              :spectrum="spectrum"
              :height="PERFORMANCE_SPECTRUM_HEIGHT"
              :range="spectrumRange"
              :active="currentSpectrum === index"
              :name="variantSegments ? variantSegments[index]?.label : null"
              :rounded-top="index === 0"
              :rounded-bottom="index === configuration?.spectra.length - 1"
              :loading="loadingConfiguration"
              @traces-clicked="onTracesClicked"
            />
        </SpectrumSelectionWrapper>
      </CardContent>
      <!-- end of actual performance spectrum view -->
    </Card>
    <SpectrumLoader v-if="!configuration?.spectra?.length" class="rounded-xl"></SpectrumLoader>
    <template v-if="!currentlyShownSpectrum?.empty">
      <Card class="mt-3 p-0">
        <CardContent class="p-0">
          <div class="-mr-1" v-if="!!configuration">
            <div class="font-bold ml-4 my-3 text-sm">Case frequency over time</div>
            <LineChart :data="performanceSpectrumChartData" :height="20"></LineChart>
          </div>
          <Skeleton v-else class="h-[80px] w-full"></Skeleton>
        </CardContent>
      </Card>

      <Card class="mt-3 p-0">
        <CardContent class="p-0">
          <div class="-mr-1" v-if="!!configuration">
            <div class="font-bold ml-4 my-3 text-sm">Case ending frequency over time</div>
            <LineChart :data="performanceSpectrumEndChartData" :height="20"></LineChart>
          </div>
          <Skeleton v-else class="h-[80px] w-full"></Skeleton>
        </CardContent>
      </Card>
    </template>

    <template v-if="!currentlyShownSpectrum?.empty">
      <Separator class="w-full mt-3"></Separator>
      <div class="font-bold text-xl mt-5 mb-5">Basic information</div>

      <statistics-view :spectrum="configuration?.spectra[currentSpectrum]"></statistics-view>
      <template v-if="currentlyShownSpectrum?.statistics?.batches">
        <Separator class="w-full mt-3"></Separator>
        <div class="font-bold text-xl mt-5 mb-5">Batch information</div>
        <batch-statistics :spectrum="currentlyShownSpectrum"></batch-statistics>
      </template>

      <Separator class="w-full mt-5"></Separator>
      <div class="font-bold text-xl mt-5">Most common Variants</div>

      <trace-view
        v-if="!!configuration"
        class="mt-10"
        :traces="configuration?.spectra[currentSpectrum].statistics.traces"
        :overall-trace-count="configuration?.spectra[currentSpectrum].statistics.traces_count"
        @selected="setVariantFilter"
      />
    </template>

    <div class="mt-10"></div>
  </div>
</template>

<script setup lang="js">

import Separator from "@/components/ui/separator/Separator.vue";
import Card from "@/components/ui/card/Card.vue";
import StatisticsView from "@/components/PerformanceSpectrumView/StatisticsView.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import PerformanceSpectrum from "@/components/PerformanceSpectrum.vue";
import {Skeleton} from "@/components/ui/skeleton";
import TraceView from "@/components/PerformanceSpectrumView/TraceView.vue";
import LineChart from "@/components/ui/LineChart.vue";
import SpectrumSelectionWrapper from "@/components/SpectrumSelectionWrapper.vue";
import {fromDate} from "@internationalized/date";
import {CANVAS_BLUE, GLOBAL_CASE_FILTER, PERFORMANCE_SPECTRUM_HEIGHT} from "@/constants.js";
import {computed} from "vue";
import {formatter} from "@/composables/useEventLogState.js";
import {CASE_FILTERS} from "@/caseFilters.js";
import {useConfigurationState} from "@/composables/useConfigurationState.js";
import BatchStatistics from "@/components/PerformanceSpectrumView/BatchStatistics.vue";
import SpectrumLoader from "@/components/PerformanceSpectrumView/SpectrumLoader.vue";

const props = defineProps({
    configurationId: {
        type: Number,
        required: true
    }
})

const {
    configuration,
    loadingConfiguration,
    currentSpectrum,
    setFilteredCases,
    setFilterDate,
    setVariantFilter,
    getFilterOfTypeForSpectrum,
    getVariantSegments,
} = useConfigurationState(props.configurationId)

const onTracesClicked = (traces) => {
    setFilteredCases(traces.map(item => item.case_ID))
}

const selectRelativeTimeSpan = ({start, end}) => {
    const min = configuration.value.spectra[0].metadata.min_timestamp
    const span = configuration.value.spectra[0].metadata.max_timestamp - min

    const date = {
        start: fromDate(new Date((min + (span * start)) * 1000)),
        end: fromDate(new Date((min + (span * end)) * 1000))
    }
    setFilterDate(date)
}



const filterDiagram = (key) => {
    const bins = configuration.value?.spectra[currentSpectrum.value].statistics[key].bins ?? []
    const data = configuration.value?.spectra[currentSpectrum.value].statistics[key].counts ?? []
    return {
        labels: bins.map((item, index) => {
            const nextItem = new Date( bins[index + 1] * 1000)
            item = new Date(item * 1000)
            if (!index){
                return `Time before and ${formatter.format(nextItem)}`
            }

            if (index === bins.length - 1){
                return `Time after and ${formatter.format(item)}`
            }
            return formatter.formatRange(item, nextItem)
        }) ?? [],
        datasets: [{label: null, data, backgroundColor: CANVAS_BLUE, borderColor: CANVAS_BLUE}],
    }
}

const performanceSpectrumChartData = computed(() => {
    return filterDiagram('frequency_diagram')
})


const spectrumRange = computed(() => {
    const min = Math.min(...configuration.value?.spectra.map(spectrum => spectrum.metadata.min_timestamp))
    const max = Math.max(...configuration.value?.spectra.map(spectrum => spectrum.metadata.max_timestamp))
    return [min, max]
})


const performanceSpectrumEndChartData = computed(() => {
    return filterDiagram('frequency_end_diagram')
})

const getGlobalCaseFilter = getFilterOfTypeForSpectrum(GLOBAL_CASE_FILTER)

const variantSegments = computed(() => {
    return getVariantSegments(getGlobalCaseFilter(CASE_FILTERS.VARIANT) ?? [])
})

const currentlyShownSpectrum = computed(() => {
    return configuration.value?.spectra[currentSpectrum.value]
})



</script>
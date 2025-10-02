<template>
  <template v-if="!!spectrum">
      <div class="grid gap-3 min-h-0" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr))">
        <StatisticsCard title="Number of cases">
          {{spectrum.statistics.case_count}}
        </StatisticsCard>

        <StatisticsCard title="Distinct activities">
          {{spectrum.statistics.activities.length}}
        </StatisticsCard>

        <StatisticsCard title="Distinct variants">
          {{spectrum.statistics.traces_count }}
        </StatisticsCard>

        <StatisticsCard title="Duration mean">
          {{formatHighestUnitTime(spectrum.metadata.mean)}}
        </StatisticsCard>
      </div>

      <Card class="w-full mt-3">
        <CardContent>
          <div class="mb-2 font-bold">Distribution of Case duration</div>
          <BarChart
            :data="chartData"
          />
        </CardContent>
      </Card>
  </template>
</template>

<script setup lang="js">

import BarChart from "@/components/ui/BarChart.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import Card from "@/components/ui/card/Card.vue";
import {computed} from "vue";
import {formatHighestUnitTime} from "@/constants.js";
import {CANVAS_BLUE} from '@/constants.js'
import StatisticsCard from "@/components/PerformanceSpectrumView/StatisticsCard.vue";

const props = defineProps({
    spectrum: {
        type: Object,
        required: true
    }
})

const chartData = computed(() => {
    return {
        labels: props.spectrum.statistics.histogram?.bins?.map((item, index) => {
            const nextItem = formatHighestUnitTime(props.spectrum.statistics.histogram.bins[index + 1])
            item = formatHighestUnitTime(item)
            if (!index){
                return `Below and ${nextItem}`
            }

            if (index === props.spectrum.statistics.histogram.bins.length - 1){
                return `Above and ${item}`
            }
            return `${item} - ${nextItem}`
        }) ?? [],
        datasets: [{label: null, data: props.spectrum.statistics.histogram?.counts, backgroundColor: CANVAS_BLUE}],
    }
})
</script>

<style scoped lang="scss">

</style>
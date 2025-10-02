<template>
  <div class="grid gap-3 min-h-0" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))">
    <StatisticsCard title="Number of batches">
      {{ batchStatistics.num_batches }}
    </StatisticsCard>

    <StatisticsCard title="Avg. batch size">
      {{ (batchStatistics.avg_size).toFixed(2) }}
    </StatisticsCard>

    <StatisticsCard title="Avg. duration">
      {{ formatDuration(batchStatistics.avg_duration) }}
    </StatisticsCard>

    <StatisticsCard title="Avg. batch interval">
      {{ formatDuration(batchStatistics.avg_batch_interval)}}
    </StatisticsCard>

    <StatisticsCard title="BF in %">
      {{ (batchStatistics.batch_frequency * 100).toFixed(2) }}%
    </StatisticsCard>
  </div>
</template>

<script setup lang="js">
import StatisticsCard from "@/components/PerformanceSpectrumView/StatisticsCard.vue";
import {computed} from "vue";

const props = defineProps({
    spectrum: {
      type: Object,
      required: true
    }
})

const batchStatistics = computed(() => {
    return props.spectrum.statistics.batches
})

function formatDuration(secondsInput) {
  let seconds = Math.floor(secondsInput);

  const days = Math.floor(seconds / 86400);
  seconds %= 86400;

  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;

  const minutes = Math.floor(seconds / 60);
  seconds %= 60;

  const parts = [];

  if (days > 0) {
    parts.push(`${days} day${days !== 1 ? 's' : ''}`);
    if (hours > 0) {
      parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
    }
  } else {
    if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
    if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
    if (seconds > 0 || parts.length === 0) {
      parts.push(`${seconds} second${seconds !== 1 ? 's' : ''}`);
    }
  }

  return parts.join(' ');
}


</script>

<style scoped lang="scss">

</style>
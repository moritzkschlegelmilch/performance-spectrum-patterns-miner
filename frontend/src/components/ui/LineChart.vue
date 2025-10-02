<template>
  <Line :data="data" :options="options"/>
</template>

<script setup lang="js">
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)

const props = defineProps({
    data: {
        type: Array,
        required: true
    }
})

const options = {
    scales: {
        x: {
            display: false,
            offset: false, // disables padding between chart edge and ticks
        },
        y: {
            display: false
        }
    },
    plugins: {
        legend: {
            display: false  // This hides the legend which includes the dataset name
        }
    }
}

</script>
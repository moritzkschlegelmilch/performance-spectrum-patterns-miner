<template>
  <Bar :data="data" :options="{...data.options, ...options}"/>
</template>

<script setup lang="js">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const options = {
    plugins: {
        legend: {
            display: false
        }
    }
}
</script>
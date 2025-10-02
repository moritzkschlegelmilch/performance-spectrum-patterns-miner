<template>
  <router-view></router-view>
</template>
<script lang="js" setup>
import {useEventLogState} from '@/composables/useEventLogState.js'

const props = defineProps({
    id: {type: Number, required: true}
})


const {currentEventLog, loadEventLog} = useEventLogState()
loadEventLog(props.id)

</script>

<style lang="scss" scoped>

</style>
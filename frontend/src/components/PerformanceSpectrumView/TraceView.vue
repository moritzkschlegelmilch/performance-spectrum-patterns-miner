<template>
  <div class="w-full">
    <div class="w-full flex flex-col">
      <template v-for="(trace, index) in traces" :key="index">
        <div class="flex gap-10 items-start hover:bg-gray-900 cursor-pointer p-4" @click="selectVariant(trace)">
          <div class="w-[200px]">
            <div class="text-gray-300 text-sm mb-2">Count</div>
            <div class="text-2xl font-bold">{{trace.count}}</div>
          </div>
          <div class="w-full min-w-0 overflow-auto">
            <div class="text-gray-300 text-sm mb-2 ml-3">Trace</div>
            <div class="flex gap-1 max-w-full overflow-auto items-center">
              <template v-for="(activity, activityIndex) in trace.trace">
                <Card class="w-[120px] flex-shrink-0 flex-grow-0 p-0">
                  <CardContent class="flex items-center p-3 h-full w-full">
                    <div class="overflow-hidden w-full" :title="activity">
                      <div class="text-gray-300 text-xs">Activity</div>
                      <div class="text-white text-sm truncate w-full" >{{activity}}</div>
                    </div>
                  </CardContent>
                </Card>
                <div class="dotted-arrow flex-shrink-0" v-if="activityIndex !== trace.trace.length - 1"></div>
              </template>
            </div>
          </div>
        </div>
        <Separator v-if="index !== traces.length - 1"></Separator>
      </template>
    </div>


    <div class="mt-5 text-center w-full text-blue-500" v-if="overallTraceCount - traces.length > 0">
      +{{overallTraceCount - traces.length}} more traces
    </div>
  </div>
</template>

<script setup lang="js">
import CardContent from "@/components/ui/card/CardContent.vue";
import Card from "@/components/ui/card/Card.vue";
import Separator from "@/components/ui/separator/Separator.vue";

const emit = defineEmits(['selected']);

const selectVariant = ({trace}) => {
  emit('selected', trace)
}

defineProps({
    traces: {
        type: Array,
        default: () => []
    },
    overallTraceCount: {
        type: Number,
        default: 0
    }
})
</script>

<style scoped lang="scss">
.dotted-arrow {
    position: relative;
    border-top: 2px dotted var(--color-gray-300);
    width: 28px;
    margin-right: 6px;
}

.dotted-arrow::after {
    content: '';
    position: absolute;
    right: -8px;
    top: -7px;
    border-width: 6px;
    border-style: solid;
    border-color: transparent transparent transparent var(--color-gray-300);
    transform: rotate(0deg);
}
</style>
<template>
  <div>
    <!-- Page view -->
    <div class="flex-col flex gap-1">
      <div class="flex items-center">
        <div>
          <div class="text-2xl font-bold flex gap-2 items-center">
            <div>Performance spectrum view</div>
            <div class="text-gray-500">/</div>
            <div v-if="!!currentEventLog" class="text-gray-500">{{ currentEventLog?.name }}</div>
            <div v-else class="text-gray-500">Loading...</div>
          </div>
          <div class="text-sm text-gray-500 w-[400px] mt-1">Welcome to the performance spectrum patterns miner. Feel
            free to experiment with the tool.
          </div>
          <router-link to="/event-logs">
            <Button class="w-fit flex gap-2 text-gray-300 cursor-pointer mt-4" variant="secondary">
              <ArrowLeft :size="18"/>
              <div class="text-sm">Back to event logs</div>
            </Button>
          </router-link>
        </div>
        <Loader2 v-if="loadingEventLogData" :size="40" class="animate-spin ml-auto"></Loader2>
      </div>
      <div class="mt-10"></div>

      <template v-if="!!currentEventLog">
        <!-- Coloring info and filter selection -->
        <filters-bar
          :configuration-id="currentEventLog?.currentConfiguration"
          class="mb-2"
          :key="currentEventLog.currentConfiguration"
        />
        <Separator v-if="inSideBySideView" class="bg-blue-500 sticky top-[62px] z-10"></Separator>
        <!-- end of coloring info -->
        <div class="w-full flex gap-3">
          <div
            v-for="(configurationId) in currentEventLog?.sideBySideConfigurations"
            :key="configurationId"
            class="w-full min-w-0"
          >
            <div class="sticky top-[63px] z-10 bg-black pb-3 pt-4" v-if="inSideBySideView">
              <div
                class="ml-2 font-bold text-sm"
                :class="configurationId === currentEventLog.currentConfiguration ? 'text-blue-500' : 'text-gray-400'"
              >
                {{getConfigurationById(configurationId).name}}
              </div>
            </div>
            <spectrum-main-view
              class="w-full shrink min-w-0"
              :configuration-id="configurationId"
            ></spectrum-main-view>
          </div>
        </div>
      </template>

    </div>
    <!-- End of Page view -->

  </div>
</template>

<script lang="js" setup>
import {ArrowLeft, Loader2} from "lucide-vue-next";
import {useEventLogState} from "@/composables/useEventLogState.js";
import Button from "@/components/ui/button/Button.vue";
import SpectrumMainView from "@/components/PerformanceSpectrumView/SpectrumMainView.vue";
import FiltersBar from "@/components/PerformanceSpectrumView/FiltersBar.vue";
import Separator from "@/components/ui/separator/Separator.vue";

const {
    currentEventLog,
    loadingEventLogData,
    inSideBySideView
} = useEventLogState()

const getConfigurationById = (id) => {
    return currentEventLog.value.configurations.find((c) => c.id === id)
}

</script>
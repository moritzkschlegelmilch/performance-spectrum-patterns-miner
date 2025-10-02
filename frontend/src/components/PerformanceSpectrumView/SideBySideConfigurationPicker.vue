<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="secondary" class="w-[60px]" :class="{'border border-blue-500': inSideBySideView}">
        <AlignHorizontalJustifyCenter />
      </Button>
    </PopoverTrigger>
    <PopoverContent>
      <div class="w-full">
        <div class="text-sm text-gray-500">Side by side spectrum</div>
        <div class="max-h-[500px] mt-3">
          <div v-for="config in currentEventLog.configurations" :key="config.id" class="flex gap-2 p-3 px-4 hover:bg-gray-900 rounded-lg items-center cursor-pointer" @click="showView(config.id)">
            <div>
              <div class="text-xs text-gray-500" >Spectrum</div>
              <div class="text-sm" :class="{'text-blue-500 font-bold': configurationIsSelected(config.id)}">{{config.name}}</div>
            </div>
            <X
              v-if="!isDeleteDisabledForConfiguration(config)"
              :size="18"
              class="ml-auto cursor-pointer"
              @click.stop="deleteConfiguration(config.id)"
            />
          </div>
        </div>


        <Dialog v-model:open="sidePickerDialogOpen">
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Choose side</DialogTitle>
              <div class="flex gap-3 mt-2">
                <Card
                  class="w-full min-w-0"
                  :class="{'border border-blue-500 text-blue-500': indexToSetViewTo === 0}"
                  @click="indexToSetViewTo = 0"
                >
                  <CardContent
                    class="flex justify-center items-center flex-col gap-1"
                  >
                    <PanelLeft />
                    <div>Left</div>
                  </CardContent>
                </Card>
                <Card
                  class="w-full min-w-0"
                  :class="{'border border-blue-500 text-blue-500': indexToSetViewTo === 1}"
                  @click="indexToSetViewTo = 1"
                >
                  <CardContent
                    class="flex justify-center items-center flex-col gap-1"
                  >
                    <PanelRight />
                    <div>Right</div>
                  </CardContent>
                </Card>
              </div>
              <div class="mt-2 flex gap-1">
                <div class="text-xs">*</div>
                <div class="text-gray-400 text-xs">
                  This will choose the side on which the configuration will be placed. The current configuration on this side
                  can of course be restored at any time but only 2 configurations can be shown at the same time.
                </div>
              </div>
            </DialogHeader>

            <DialogFooter>
              <Button @click="setViewToSelectedSide()">Replace</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog v-model:open="nameDialogOpen">
          <DialogTrigger as-child>
            <Button class="mt-3 w-full">
              Add view
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add View</DialogTitle>
              <Input placeholder="Name" v-model="newSpectrumName" class="mt-2"/>
            </DialogHeader>

            <DialogFooter>
              <Button :disabled="!newSpectrumName" @click="addView">Add</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="js">
import {useEventLogState} from "@/composables/useEventLogState.js";
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog'
import {AlignHorizontalJustifyCenter, X, PanelLeft, PanelRight} from 'lucide-vue-next'
import {computed, ref} from "vue";
import Button from "@/components/ui/button/Button.vue";
import Input from "@/components/ui/input/Input.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import {Popover, PopoverContent, PopoverTrigger} from "@/components/ui/popover/index.js";

const {currentEventLog, deleteConfiguration, addConfiguration, setConfigurationView, inSideBySideView} = useEventLogState()

const newSpectrumName = ref('')
const nameDialogOpen = ref(false)
const sidePickerDialogOpen = ref(false)
const indexToSetViewTo = ref(0)
const configurationIdToBeSet = ref('')

const configurationIsSelected = (configurationId) => {
  return currentEventLog.value.sideBySideConfigurations.includes(configurationId)
}

const showView = (id) => {
    if (configurationIsSelected(id)) return;

    if (!inSideBySideView.value) {
        setConfigurationView(1, id)
        return;
    }
    configurationIdToBeSet.value = id
    indexToSetViewTo.value = 0
    sidePickerDialogOpen.value = true
}

const setViewToSelectedSide = () => {
    setConfigurationView(indexToSetViewTo.value, configurationIdToBeSet.value)
    sidePickerDialogOpen.value = false
}

const addView = () => {
    addConfiguration(newSpectrumName.value)
    newSpectrumName.value = ''
    nameDialogOpen.value = false
}

const isDeleteDisabledForConfiguration = (spectrum) => {
    return !inSideBySideView.value && configurationIsSelected(spectrum.id)
}

</script>

<style scoped lang="scss">

</style>
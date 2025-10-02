<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :class="{
          'w-[260px] justify-start text-left font-normal': true,
          'text-muted-foreground': !value
        }"
      >
        <CalendarIcon class="mr-2 h-4 w-4" />
        <template v-if="value.start">
          <template v-if="value.end">
            {{ df.format(value.start.toDate(getLocalTimeZone())) }} - {{ df.format(value.end.toDate(getLocalTimeZone())) }}
          </template>

          <template v-else>
            {{ df.format(value.start.toDate(getLocalTimeZone())) }}
          </template>
        </template>
        <div v-else class="text-gray-500">
          No date range set
        </div>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0">
      <RangeCalendar v-model="value" initial-focus :number-of-months="2" @update:start-value="(startDate) => value.start = startDate" />
      <div class="p-2 flex gap-2 w-full">
        <Button class="min-w-0 w-full shrink" variant="secondary" @click="resetValue">Reset</Button>
        <Button class="min-w-0 w-full shrink" @click="emit('apply')">Apply</Button>
      </div>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="js">

import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { RangeCalendar } from '@/components/ui/range-calendar'
import {
    DateFormatter,
    getLocalTimeZone,
} from '@internationalized/date'
import { CalendarIcon } from 'lucide-vue-next'

const df = new DateFormatter('en-US', {
    dateStyle: 'medium',
})

const emit = defineEmits('applied')

const value = defineModel({
    type: Object,
    default:{
        start: null,
        end: null,
    }
})
const resetValue = () => {
    value.value = {
        start: null,
        end: null,
    }
    emit('apply')
}
</script>

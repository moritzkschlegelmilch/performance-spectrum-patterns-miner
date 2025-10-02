<template>
  <Combobox v-model="value" by="label">
    <ComboboxAnchor as-child>
      <ComboboxTrigger as-child>
        <Button variant="outline" class="justify-between w-full min-w-0" :disabled="disabled">
          <slot name="item" v-bind="{option: value}" v-if="!!value"><div class="overflow-ellipsis w-full overflow-hidden">{{ value.label }}</div></slot>
          <div v-else>{{placeholder}}</div>
          <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxList class="w-[270px]">
      <div class="relative items-center" v-if="showSearchBar">
        <ComboboxInput class="pl-3 focus-visible:ring-0 border-0 border-b rounded-none h-10" placeholder="Select option..." />
      </div>

      <ComboboxEmpty>
        No option available.
      </ComboboxEmpty>

      <ComboboxGroup class="max-h-[300px] overflow-auto">
        <ComboboxItem
          class="py-2"
          v-for="option in options"
          :key="option.key"
          :value="option"
        >
          <slot name="item" v-bind="{option}">{{ option.label }}</slot>

          <ComboboxItemIndicator v-if="value?.key === option.key">
            <Check class="ml-auto h-4 w-4" />
          </ComboboxItemIndicator>
        </ComboboxItem>
      </ComboboxGroup>
    </ComboboxList>
  </Combobox>
</template>

<script setup lang="js">
import { Button } from '@/components/ui/button/index.js'
import { Combobox, ComboboxAnchor, ComboboxEmpty, ComboboxGroup, ComboboxInput, ComboboxItem, ComboboxItemIndicator, ComboboxList, ComboboxTrigger } from '@/components/ui/combobox/index.js'
import { Check, ChevronsUpDown, Search } from 'lucide-vue-next'

defineProps({
    options: {
        type: Array,
        required: true
    },
    placeholder: {
        type: String,
        default: 'Select an option'
    },
    showSearchBar: {
        type: Boolean,
        default: false
    },
    disabled: {
        type: Boolean,
        default: false
    }
})

const value = defineModel({required: true})
</script>
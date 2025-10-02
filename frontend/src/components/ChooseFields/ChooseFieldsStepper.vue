<template>
  <Stepper :model-value="step" class="flex w-full justify-between gap-15">
    <StepperItem
      v-for="(step) in steps"
      :key="step.step"
      v-slot="{ state }"
      :step="step.step"
      class="relative flex w-full flex-col justify-center"
    >
      <StepperSeparator
        v-if="step.step !== steps[steps.length - 1].step"
        class="absolute left-[calc(50%+64px)] right-[calc(-50%+10px)] top-5 block h-0.5 shrink-0 rounded-full bg-muted group-data-[state=completed]:bg-primary"
      />

      <div>
        <Button
          :class="[state === 'active' && 'ring-2 ring-ring ring-offset-2 ring-offset-background']"
          :variant="state === 'completed' || state === 'active' ? 'default' : 'outline'"
          class="z-10 rounded-full shrink-0"
          size="icon"
        >
          <Check v-if="state === 'completed'" class="size-5"/>
          <Circle v-if="state === 'active'"/>
          <Dot v-if="state === 'inactive'"/>
        </Button>
      </div>

      <div class="flex flex-col items-center text-center">
        <StepperTitle
          :class="[state === 'active' && 'text-primary']"
          class="text-sm font-semibold transition lg:text-base"
        >
          {{ step.title }}
        </StepperTitle>
        <StepperDescription
          :class="[state === 'active' && 'text-primary']"
          class="sr-only text-xs text-muted-foreground transition md:not-sr-only lg:text-sm"
        >
          {{ step.description }}
        </StepperDescription>
      </div>
    </StepperItem>
  </Stepper>
</template>

<script lang="js" setup>
import {Button} from '../ui/button'

import {Stepper, StepperDescription, StepperItem, StepperSeparator, StepperTitle} from '../ui/stepper'
import {Check, Circle, Dot} from 'lucide-vue-next'

defineProps({
    step: {
        type: Number,
        default: 1
    },
    steps: {
        type: Array,
        default: () => []
    }
})
</script>
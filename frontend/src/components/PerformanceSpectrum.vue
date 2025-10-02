<template>
  <div ref="container"
       :style="{height: height+'px'}"
       class="bg-gray-800 relative overflow-visible"
       :class="{'rounded-t-xl': roundedTop, 'rounded-b-xl': roundedBottom}"
       @mouseleave="onMouseLeave"
       @mousemove="onHover"
       @mousedown="onMousedown"
       @mouseup="onMouseup"
  >
      <div class="absolute bottom-0 border-1 border-gray-500 w-full" v-if="!roundedBottom"></div>
      <div class="absolute top-0 right-0 mr-3 mt-3 px-3 py-2 rounded-sm bg-gray-900/50 text-sm" v-if="name && !loading">
        {{name}}
      </div>
      <div
        v-if="(spectrum?.empty || !absoluteDuration) && !loading"
        class="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] font-bold flex gap-2 items-center"
      >
        <AlertCircle :size="18"></AlertCircle>
        {{!spectrum?.empty ? 'Selection is singularity' : 'Selection is empty'}}
      </div>
      <div
        :class="{
          'rounded-t-xl': roundedTop,
          'rounded-b-xl': roundedBottom,
        }"
        class="overflow-hidden h-full"
        v-show="!loading"
      >
        <div
          v-if="active"
          :class="{
            'rounded-t-xl': roundedTop,
            'rounded-b-xl': roundedBottom,
          }"
          class="absolute pointer-events-none border-2 border-blue-500 w-full h-full top-0 left-0">
        </div>
        <canvas ref="canvasRef"></canvas>
      </div>
      <!-- tooltip card -->
      <Card
        v-if="!leftView && (hoveredCases.length || calculating) && !rectangleSelectActive && !loading"
        :style="tooltipPosition"
        class="absolute z-10 p-0"
      >
        <CardContent class="p-3 w-[200px]">
          <div class="flex gap-2">
            <div>
              <div class="text-sm font-bold">{{ !hoveredCases.length ? 'Calculating cases' : 'Cases selected' }}</div>
              <div class="text-xs text-gray-500">Highlighted in blue</div>
            </div>
            <Loader2 v-if="!hoveredCases.length" class="ml-auto animate-spin"></Loader2>
          </div>
          <div v-if="hoveredCases.length">
            <div class="flex gap-2 items-center mt-2">
              <div class="dot"></div>
              <div class="text-xs text-gray-300"><span class="text-white font-bold">{{ hoveredCases.length }}</span>
                cases selected
              </div>
            </div>
            <div class="text-blue-500 text-xs mt-3">Click to see in isolation</div>
          </div>
        </CardContent>
      </Card>
    <SpectrumLoader v-if="loading"></SpectrumLoader>
  </div>
</template>

<script lang="js" setup>
import {computed, inject, onMounted, onUnmounted, ref, watch} from "vue";
import {debounce} from "lodash";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import {Loader2, AlertCircle} from "lucide-vue-next";
import {CANVAS_BLUE, QUARTILE_COLORS} from "@/constants.js";
import SpectrumLoader from "@/components/PerformanceSpectrumView/SpectrumLoader.vue";

const props = defineProps({
    spectrum: {
        type: Object,
        required: true
    },
    height: {
        type: Number,
        default: 300
    },
    range: {
        type: Array,
        required: true
    },
    active: {
        type: Boolean,
        default: false
    },
    roundedTop: {
        type: Boolean,
        default: false
    },
    roundedBottom: {
        type: Boolean,
        default: false
    },
    name: {
        type: String,
        default: null
    },
    loading: {
        type: Boolean,
        default: false
    }
})


let entry_map = new Map()
watch(() => props.spectrum, () => {
    entry_map = new Map()
    props.spectrum.records.forEach(record => {
        entry_map.set(record.case_ID, record)
    })
}, {immediate: true})

const emit = defineEmits(['traces-clicked'])

// reference to the container
const container = ref(null);

// True if the mouse is currently not on the performance spectrum
const leftView = ref(true)

// Compute the absolute distance between min and max timestamp (used for line computation)
const absoluteDuration = computed(() => {
    if (props.range){
        return props.range[1] - props.range[0]
    }
})

// Cases that the mouse is currently hovering
const hoveredCases = inject('hoveredCases', ref([]))

// True if the tooltip is shown but computations for intersections are not done yet
const calculating = ref(false)

// HTMLElement Ref for the canvas that displays the spectrum
const canvasRef = ref(null)

// Line thickness based on which we compute intersection with mouse and lines
const lineThickness = 4;

// Function to show the tooltip and compute the intersection with the lines
const showTooltip = (xPos, yPos) => {
    if (leftView.value || !props.spectrum?.records || !container.value || rectangleSelectActive.value) return;
    hoveredCases.value = []
    const width = container.value.clientWidth;
    // Find the record that the mouse is hovering over
    const hoveredRecords = props.spectrum.records.filter(record => {
        // Do a simple check with the hitbox of the line first
        const x1 = ((record.start_timestamp - props.range[0]) / absoluteDuration.value) * width;
        const x2 = width * ((record.end_timestamp - props.range[0]) / absoluteDuration.value);

        // Check if the mouse is within the horizontal range of the line
        if (xPos < (x1 - 5) || xPos > (x2 + 5)) return false

        if (x1 === x2) return true
        // Do an advanced check with the slope of the line, i.e. if the mouse is actually hovering over the line
        const y1 = 0; // Vertical start of the line
        const y2 = props.height; // Vertical end of the line

        if (Math.abs(x2 - x1) < 10) return true
        // Check if mouse is within the vertical range of the line (considering the line's "thickness")
        const slope = (y2 - y1) / (x2 - x1); // Calculate the slope of the line
        const expectedY = slope * (xPos - x1); // Get the expected Y value at mouse X position

        return Math.abs(yPos - expectedY) <= lineThickness;
    });

    if (hoveredRecords.length) {
        hoveredCases.value = hoveredRecords
    }
    calculating.value = false
}

// Debounce the tooltip showing function to avoid too many calls (this would crash the browser for large event logs)
const debounceShowingTooltip = debounce(showTooltip, 500);
// Position of the tooltip relative to the boundaries of the container
const tooltipPosition = ref({
    left: '0px',
    top: '0px'
})

// Simple on hover. Calculate the tooltip position here and call the debounced intersection function
const onHover = (event) => {
    if (!container.value) return;

    leftView.value = false
    // Get the mouse position relative to the container
    const containerRect = container.value.getBoundingClientRect();
    const mouseX = event.clientX - containerRect.left; // Mouse x position relative to container
    const mouseY = event.clientY - containerRect.top; // Mouse y position relative to container
    tooltipPosition.value = {
        left: mouseX + 'px',
        top: mouseY + 'px'
    }

    calculating.value = true
    // Call debounced function with both x and y mouse positions
    debounceShowingTooltip(mouseX, mouseY);
}

const getColorByQuartile = (duration) => {
    const [q1, q2, q3] = Object.values(props.spectrum.metadata.quartiles);
    if (duration <= q1) return QUARTILE_COLORS.BLUE;
    if (duration <= q2) return QUARTILE_COLORS.YELLOW;
    if (duration <= q3) return QUARTILE_COLORS.ORANGE;
    return QUARTILE_COLORS.RED;
};

const scaleLineWidth = (lowerBound, upperBound) => {
    const range = upperBound - lowerBound;
    const scalingFactor = Math.exp(-5)
    return lowerBound + range*(Math.exp(-scalingFactor*props.spectrum.records.length))
}

const drawSpectrum = () => {
    if (!canvasRef.value || rectangleSelectActive.value || props.loading) return;
    const ctx = canvasRef.value.getContext('2d');

    // Clear the canvas to redraw
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    const width = container.value.clientWidth;
    const height = props.height;

    // Set canvas size (resolution to match the container div)
    canvasRef.value.width = width;
    canvasRef.value.height = height;

    // local function to draw a single line to the spectrum
    const drawLine = (lineWidth, opacity = 1) => (record, color) => {
        // Calculate starting point

        let x1, x2;
        x1 = ((record.start_timestamp - props.range[0]) / absoluteDuration.value) * width;
        // Calculate endpoint
        x2 = width * (record.end_timestamp - props.range[0]) / absoluteDuration.value;


        // Use the canvas interface to actually draw the line
        ctx.beginPath();
        ctx.moveTo(x1, 0);
        ctx.lineTo(x2, height);
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth
        ctx.opacity = opacity
        ctx.stroke();
    }

    const drawRegularLine = drawLine(scaleLineWidth(0.1, 1), 0.5);
    // Draw all lines
    props.spectrum.records.forEach((record) => drawRegularLine(record, getColorByQuartile(record.duration)));

    const drawHighlightedLine = drawLine(1, 1);
    // Draw the highlighted lines with different attributes
    hoveredCases.value.forEach((record => {
        const foundRecord = entry_map.get(record.case_ID)
        drawHighlightedLine(foundRecord, CANVAS_BLUE);
    }))
}

// Rerender the spectrum when changed
watch(() => props.spectrum, () => {
    drawSpectrum();
})

watch(hoveredCases, () => {
    drawSpectrum();
})

const hideTooltip = () => {
    leftView.value = true;
    hoveredCases.value = [];
    calculating.value = false;
}

let resizeObserver;
onMounted(() => {
    resizeObserver = new ResizeObserver(() => {
        drawSpectrum();
    });
    resizeObserver.observe(container.value);
    document.addEventListener('scroll', hideTooltip)
    drawSpectrum()
})

onUnmounted(() => {
    resizeObserver.disconnect()
    document.removeEventListener('scroll', hideTooltip)
})

const timedOut = ref(false)
const onMousedown = () => {
    timedOut.value = false
    setTimeout(() => {
        timedOut.value = true
    }, 100)
}

// Function that is called when the user clicks on the line
const onMouseup = () => {
    if (!timedOut.value && hoveredCases.value.length) {
        emit('traces-clicked', hoveredCases.value)
    }
    hoveredCases.value = []
}

const onMouseLeave = () => {
    leftView.value = true;
}

const rectangleSelectActive = inject('rectangleSelectActive', ref(false))


</script>
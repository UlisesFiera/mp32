<script lang="ts">
    import type { LayoutProps } from './$types';
    import DotField from '#lib/components/svelte-bits/DotField.svelte';
    import Rings from '#lib/components/svelte-bits/MagicRings.svelte';

    let { children }: LayoutProps = $props();
</script>

<div class="relative min-h-screen overflow-hidden">
    <div class="absolute inset-0 z-0">
        <DotField
            dotRadius={0.7}
            dotSpacing={10}
            cursorRadius={10}
            cursorForce={1}
            bulgeOnly={false}
            bulgeStrength={0}
            glowRadius={10}
            sparkle={false}
            waveAmplitude={0}
            gradientFrom="#ffdd00"
            gradientTo="#ffb089"
            glowColor="#14110e"
        />
    </div>
    <div class="absolute inset-0 z-0">
        <Rings
            color="#fbfda4"
            colorTwo="#fafc91"
            speed={0.2}
            ringCount={1}
            attenuation={10}
            lineThickness={1}
            baseRadius={0.1}
            radiusStep={0.1}
            scaleRate={1}
            opacity={0.4}
            blur={0}
            noiseAmount={0}
            rotation={0}
            ringGap={1.5}
            fadeIn={0.2}
            fadeOut={0.5}
            followMouse={false}
            mouseInfluence={0}
            hoverScale={0}
            parallax={0}
            clickBurst={false}
        />
    </div>
    <div class="absolute inset-0 z-10 bg-gradient-to-t from-black to-black/10"></div>
    <div class="relative z-10">
        {@render children()}
    </div>
</div>

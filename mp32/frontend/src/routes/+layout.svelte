<script lang="ts">
    import './layout.css';
    import favicon from '#lib/assets/favicon.svg';
    import type { LayoutProps } from './$types';
    import DotField from '#lib/components/svelte-bits/DotField.svelte';
    import Rings from '#lib/components/svelte-bits/MagicRings.svelte';

    let { children }: LayoutProps = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<div class="relative min-h-screen overflow-hidden">
    <div class="absolute inset-0 z-0 blur-md">
        <DotField
            dotRadius={5.7}
            dotSpacing={20}
            cursorRadius={700}
            cursorForce={0.42}
            bulgeOnly={true}
            bulgeStrength={59}
            glowRadius={20}
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
        speed={0.5}
        ringCount={5}
        attenuation={10}
        lineThickness={2}
        baseRadius={0.1}
        radiusStep={0.1}
        scaleRate={0.1}
        opacity={0.1}
        blur={0}
        noiseAmount={0.1}
        rotation={0}
        ringGap={1.5}
        fadeIn={0.7}
        fadeOut={0.5}
        followMouse={true}
        mouseInfluence={0.2}
        hoverScale={1.2}
        parallax={0.05}
        clickBurst={true}
      />
    </div>
    <div class="absolute inset-0 z-10 bg-gradient-to-t from-black to-black/10">
    </div>
    <div class="relative z-10">
        {@render children()}
    </div>
</div>
<script lang="ts">
    import './layout.css';
    import favicon from '#lib/assets/favicon.svg';
    import type { LayoutProps } from './$types';
    import DotField from '#lib/components/svelte-bits/DotField.svelte';

    let { children }: LayoutProps = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<div class="relative min-h-screen overflow-hidden">
    <div class="absolute inset-0 z-0">
        <DotField
            dotRadius={0.7}
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

    <div class="relative z-10">
        {@render children()}
    </div>
</div>
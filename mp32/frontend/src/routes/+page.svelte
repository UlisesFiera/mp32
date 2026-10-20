<script lang="ts">
    import { ArrowUpRight } from 'lucide-svelte';
</script>

<div class="min-h-screen flex items-center justify-center">
    <div class="z-10 flex flex-col w-fit items-center justify-center gap-4 p-7 rounded-xl bg-gradient-to-t from-neutral-900 to-neutral-800">
        <form class="w-64 space-y-4">
            <fieldset class="space-y-2 text-surface-100">
                <legend>Login</legend>

                <label class="gap-1 flex flex-col text-xs">
                    <span>User</span>
                    <input class="input text-xs rounded-xl bg-surface-500 focus:border-yellowbrand-400/50" type="user"/>
                </label>

                <label class="gap-1 flex flex-col text-xs">
                    <span>Password</span>
                    <input class="input text-xs rounded-xl bg-surface-500" type="password"/>
                </label>
            </fieldset>
        </form>

        <div class="flex items-center gap-4">
            <button type="button" class="btn preset-filled text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand">
                <span>log-in</span>
            </button>
            <button type="button" class="btn preset-filled text-xs bg-surface-500 text-surface-100 rounded-xl hover:text-black hover:bg-yellowbrand">
                <span>sign-up</span>
                <ArrowUpRight size={16} />
            </button>
        </div>
    </div>
</div>
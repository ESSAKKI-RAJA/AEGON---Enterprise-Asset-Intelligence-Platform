import { createServerClient } from "@supabase/ssr";
// @ts-ignore — vinxi/http is a runtime-only Vinxi API without TS declarations
import { getCookie, setCookie } from "vinxi/http";

const supabaseUrl = process.env.VITE_SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_PUBLISHABLE_KEY || import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

export const createClient = () => {
  return createServerClient(
    supabaseUrl!,
    supabaseKey!,
    {
      cookies: {
        get(name: string) {
          return getCookie(name);
        },
        set(name: string, value: string, options: any) {
          try {
            setCookie(name, value, options);
          } catch {
            // The `set` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
        remove(name: string, options: any) {
          try {
            setCookie(name, "", { ...options, maxAge: 0 });
          } catch {
            // The `remove` method was called from a Server Component.
          }
        },
      },
    },
  );
};

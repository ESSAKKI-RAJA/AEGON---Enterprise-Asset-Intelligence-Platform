import { createServerClient } from "@supabase/ssr";
// @ts-ignore — vinxi/http is a runtime-only Vinxi API without TS declarations
import { getCookie, setCookie, getRequestHeaders } from "vinxi/http";

const supabaseUrl = process.env.VITE_SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_PUBLISHABLE_KEY || import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

export const updateSession = async () => {
  let supabaseResponse: any = null;

  const supabase = createServerClient(
    supabaseUrl!,
    supabaseKey!,
    {
      cookies: {
        get(name: string) {
          return getCookie(name);
        },
        set(name: string, value: string, options: any) {
          setCookie(name, value, options);
        },
        remove(name: string, options: any) {
          setCookie(name, "", { ...options, maxAge: 0 });
        },
      },
    },
  );

  // refreshing the auth token
  await supabase.auth.getUser();

  return supabaseResponse;
};

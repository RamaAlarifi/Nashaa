# Sprint 1 interface

The approved palette is Emerald #087F5B, Deep Navy #132A3A, Turquoise #20BFA9, Warm Gold #E9B949, Soft Sand #F7F5EF, and White #FFFFFF. Supporting text uses #4E5F6B or #C8D0D4. Interface text uses Poppins; the original SVGs preserve both outlined wordmarks. Logo spacing/minimum widths are implemented in `Logo.tsx`; supplied icon and favicon files are used directly.

Screens: landing, registration, login, password recovery/reset, role dashboard, profile, idea list, creation, idea detail/edit, assessment and visibility controls. Non-owner shared links display only permitted summaries. Owner navigation contains Overview, My ideas, My profile; other roles have Overview and My profile.

Inputs are labeled, keyboard focus is visible, errors/status are announced, navigation marks the current page, and reduced-motion preferences are respected. Layouts adapt through mobile-first Tailwind breakpoints. Validate keyboard use and mobile rendering in a connected browser before client acceptance.

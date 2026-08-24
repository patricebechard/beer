# Beer

A pint of lager that lives in your phone — the old iBeer trick, rebuilt as a web app. The beer fills the whole screen, edge to edge: hold your phone upright and it fills; tilt it back and you drink it, faster the further you tilt. Built as a Progressive Web App (PWA) — install it to your home screen and drink offline, no app store needed. No ads, no analytics, no tracking.

**Pour one now: [patricebechard.com/beer](https://patricebechard.com/beer/)**

## Features

- **Tilt to drink** — the pour rate scales with how far you tip the phone, from a slow sip at 25° to chugging it flat out in a couple of seconds
- **It only spills what clears the rim** — tilt a half-full screen and nothing leaves; the beer runs out only once the surface actually reaches the lip, so you have to keep tipping further to finish it
- **Hold upright to fill** — an empty glass refills whenever you bring the phone back to vertical
- **Five things on tap** — Michelob Ultra, Pliny the Elder, HYPA, Guinness and a Clamato Caesar, each with its own colour, clarity, head and carbonation, and a line about what you're drinking; tap the logo in the corner to switch
- **Split the G** — pick the Guinness and a dashed line appears across the bar of the G. Start from a full pint, take one gulp, and stop with the stout meeting the collar exactly on that line: bring the phone back upright and a scorecard grades the attempt out of 100, tells you how many millimetres you were out, and remembers your best
- **Your phone is the glass** — no vessel drawn around it: the beer runs to all four edges, the brand logo is printed on the front in front of the liquid, and light rakes down the sides
- **Real liquid surface** — the beer stays level with the actual horizon no matter how you hold the phone, and the volume is conserved exactly as the surface tilts
- **No screen flipping** — tilting sideways is exactly the motion that makes a phone rotate to landscape, so the app cancels the rotation out and stays glued to the phone
- **Foam head** — builds while you pour, froths up when you drink, then settles
- **Sloshing** — a damped spring tips and ripples the surface when you move the glass
- **Carbonation** — bubbles rise against real gravity and pop into the head
- **Stays awake** — holds a screen wake lock so the display doesn't sleep mid-pint
- **Works on a laptop** — with no motion sensor, drag or use the arrow keys to tilt the glass
- **Offline support** — works without an internet connection after first load
- **Installable** — add to your home screen for a full-screen, app-like experience

## Controls

| | |
|---|---|
| Phone upright | Fill it up |
| Tilt the phone | Drink — the more tilt, the faster it pours |
| Tap the screen | Top it up |
| Drag / arrow keys | Tilt, when there's no motion sensor |
| `R` or `0` | Level it out |
| `Space` | Top it up |
| Badge, top right | Pick your drink |
| `B` | Next drink |
| `Esc` | Close the menu |

On iOS the browser asks permission before it will report motion — that's what the **POUR** button on the intro screen is for.

## Running locally

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser. Motion sensors need HTTPS (or localhost), so to try it on a real phone, serve it over HTTPS or open it from the deployed URL.

## Installing on your phone

1. Open the URL in your phone's browser (Safari on iOS, Chrome on Android)
2. **iOS**: tap Share > "Add to Home Screen"
3. **Android**: tap Menu > "Add to Home Screen" or "Install app"

The app will appear as a standalone app on your home screen.

## Trademarks

The drink names and logos are the trademarks of their respective owners, used
here only to identify what you are pretending to drink. This is a personal
project with no affiliation to, or endorsement from, any of them.

## Notes

The app icons are generated, not drawn — run `python3 make_icons.py` to rebuild them.

The drink logos come from the brand art in `pint_logos/`. `python3 make_logos.py` keys out each background (flat colour, or a circular mask where the logo is a disc), trims the transparent margin and scales the result down to `logo-*.png`. Those same files are used both for the print on the glass and for the tiles in the picker.

Orientation comes from `deviceorientation`'s `beta`/`gamma`, converted to a gravity vector in the device's own frame. Tilt is the angle between the screen's up axis and world up, so it reads 0° upright and 90° flat on a table, whichever way you spin the phone about its own axis. The liquid is drawn in a frame rotated to align with gravity, and the surface height is solved by bisection against the screen outline so the volume on screen always matches the fill level.

Beer leaves the screen only when the surface plane actually clears the rim, which is the top edge. Rolling sideways is solved exactly: the lower of the two top corners is the lip, and the retained volume is the area of the screen below that line. Tipping the phone away from you leaves the on-screen surface flat, so that axis uses the closed form for a box of depth `DEPTH` tipped by the out-of-plane angle — a wedge of liquid slides out across the floor and spills once it clears the lip. The two factors multiply, which is exact whenever either axis is upright. The upshot is that a half-full screen leaks nothing at 45°, and finishing a pint means tipping past about 85°.

Split the G scores where the beer line ends up, not how you got there. The G is printed on the glass by the logo, so its bar is at a fixed height on screen — `splitG` in the Guinness entry is how far down the logo art the bar sits (0.896, measured off the pixels of `logo-guinness.png`). An attempt arms at 98% full, begins the moment the level starts dropping, and is called once the pour has stopped and the phone is back within 28° of upright for half a second, so only one gulp counts. The line is read the way you'd read it in the pub — glass upright, where the stout meets the collar — which is the liquid surface, so the foam's `HEADROOM` comes off the fill first. The miss is a Gaussian: about 3% of the screen height out scores 61%, and it's converted to millimetres against the ~150 mm of liquid in a real pint.

Phones auto-rotate to landscape as soon as you tip them far enough sideways, which is the same motion you use to drink. A page can't refuse that — orientation locks need fullscreen, and iOS Safari has no Fullscreen API — so the app counter-rotates itself by the same amount to cancel it out. Which way to spin is read off gravity rather than `screen.orientation.angle`, whose sign is inconsistent across platforms: if the device's right edge is down, its top edge points to the viewer's right, so the content turns +90° to line back up with the phone.

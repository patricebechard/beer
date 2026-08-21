# Beer

A pint of lager that lives in your phone — the old iBeer trick, rebuilt as a web app. Hold your phone upright and the glass fills; tilt it back and you drink it, faster the further you tilt. Built as a Progressive Web App (PWA) — install it to your home screen and drink offline, no app store needed. No ads, no analytics, no tracking.

**Pour one now: [patricebechard.com/beer](https://patricebechard.com/beer/)**

## Features

- **Tilt to drink** — the pour rate scales with how far you tip the phone, from a slow sip at 25° to chugging it upside down in under two seconds
- **Hold upright to fill** — an empty glass refills whenever you bring the phone back to vertical
- **Real liquid surface** — the beer stays level with the actual horizon no matter how you hold the phone, and the volume is conserved exactly as the surface tilts
- **Foam head** — builds while you pour, froths up when you drink, then settles
- **Sloshing** — a damped spring tips and ripples the surface when you move the glass
- **Carbonation** — bubbles rise against real gravity and pop into the head
- **Synthesised sound** — glugs, fizz and a closing burp, all generated with the Web Audio API; there isn't an audio file in the repo
- **Haptics** — a tap per glug on devices that support vibration
- **Beers counted** — every pint you finish is tallied and saved
- **Stays awake** — holds a screen wake lock so the display doesn't sleep mid-pint
- **Works on a laptop** — with no motion sensor, drag or use the arrow keys to tilt the glass
- **Offline support** — works without an internet connection after first load
- **Installable** — add to your home screen for a full-screen, app-like experience

## Controls

| | |
|---|---|
| Phone upright | Fill the glass |
| Tilt the phone | Drink — the more tilt, the faster it pours |
| Tap the glass | Top it up |
| Drag / arrow keys | Tilt, when there's no motion sensor |
| `R` or `0` | Level the glass |
| `Space` | Top it up |
| `M` | Mute |

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

## Notes

The icons are generated, not drawn — run `python3 make_icons.py` to rebuild them.

Orientation comes from `deviceorientation`'s `beta`/`gamma`, converted to a gravity vector. Tilt is the angle between the screen's up axis and world up, so it reads 0° upright and 90° flat on a table, whichever way you spin the phone about its own axis. The liquid is drawn in a frame rotated to align with gravity, and the surface height is solved by bisection against the glass outline so the volume on screen always matches the fill level.

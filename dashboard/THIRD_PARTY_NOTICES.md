# Watermelon UI

`src/components/ContinuousTabs.jsx` adapts the official Continuous Tabs source:
https://registry.watermelon.sh/r/continuous-tabs.json

Project: https://github.com/WatermelonCorp/watermelon-platform
The component is distributed under the MIT license. The original implementation
uses Tailwind classes; this adaptation uses dashboard CSS variables, controlled
state, accessible pressed buttons, and a unique LayoutGroup per instance.

`src/components/ScrollResearchCard.jsx` adapts the rotateX, progressive blur,
and perspective composition from the Fund Widget's FundCard implementation:
https://registry.watermelon.sh/r/fund-widget.json
The adaptation uses scroll progress, conservative rotations, and research content
instead of a draggable fund selector. `MarketChartBackdrop.jsx` is an original
canvas renderer of the exported monthly equal-weight industry return index.

MIT License

Copyright (c) 2026 Watermelon Platform Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

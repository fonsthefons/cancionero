// Keep the top bar and the menu at normal size and on screen while pinch-zoomed.
//
// Pinch-zoom magnifies the whole page, and the browser keeps "fixed" and
// "sticky" elements attached to the unzoomed page, so the top bar grew and
// slid out of view. Here we follow the zoomed view (visualViewport) and set
// --unzoom to a transform that moves the bar and menu to its top-left corner
// and shrinks them back by the zoom factor; styles.css applies it.

const PINCH_ZOOM = {
    minScale: 1.01, // below this the page counts as not zoomed
};

let pinchZoomFrame = 0;

function updatePinchZoom() {
    pinchZoomFrame = 0;
    const view = window.visualViewport;
    const root = document.documentElement.style;
    if (!view || view.scale < PINCH_ZOOM.minScale) {
        root.removeProperty("--unzoom");
        return;
    }
    root.setProperty("--unzoom",
        `translate(${view.offsetLeft}px, ${view.offsetTop}px) scale(${1 / view.scale})`);
}

function schedulePinchZoom() {
    if (!pinchZoomFrame) pinchZoomFrame = requestAnimationFrame(updatePinchZoom);
}

if (window.visualViewport) {
    visualViewport.addEventListener("resize", schedulePinchZoom);
    visualViewport.addEventListener("scroll", schedulePinchZoom);
    window.addEventListener("scroll", schedulePinchZoom, { passive: true });
    updatePinchZoom();
}

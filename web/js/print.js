// Print dialog: choose columns and chords, then open the browser print.

const printDialog = document.getElementById("print-dialog");

onAction("open-print", () => printDialog.showModal());

printDialog.addEventListener("close", () => {
    if (printDialog.returnValue !== "print") return;
    const form = printDialog.querySelector("form");
    document.body.dataset.printColumns = form.columns.value;
    document.body.dataset.printChords = form.chords.value;
    window.print();
});

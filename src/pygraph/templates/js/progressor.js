// Progress Bar
const progressContainer = document.getElementById('progressContainer')
const progressBar = document.getElementById('progressBar')

let setProgressBar = (visibility, percent) => {
    progressContainer.style.visibility = visibility
    progressBar.style.width = `${percent}%`
};
let hideProgressBar = () => setProgressBar('hidden', 0);
let showProgressBar = (percent) => setProgressBar('visible', percent);

network.on('stabilizationProgress', (event) => {showProgressBar((event.iterations / event.total) * 100)});
network.on('stabilizationIterationsDone', hideProgressBar);
network.on('stabilized', hideProgressBar);
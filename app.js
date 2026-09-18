// --- CONFIGURATION ---
const sequenceLength = 30;
const features = 225; // 99 (Pose) + 63 (Left Hand) + 63 (Right Hand)
const actions = ['hello', 'thanks', 'iloveyou'];
const confidenceThreshold = 75.0; // Ignore predictions below this %

let model;
let sequence = [];

const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');
const statusText = document.getElementById('status');
const predictionText = document.getElementById('prediction');

// --- 1. LOAD TENSORFLOW MODEL ---
async function loadModel() {
    try {
        model = await tf.loadLayersModel('./tfjs_model/model.json');
        statusText.innerText = 'Model & Camera Active! Ready to sign.';
        statusText.style.color = 'green';
    } catch (error) {
        console.error('Failed to load model:', error);
        statusText.innerText = 'Error loading model.';
        statusText.style.color = 'red';
    }
}
loadModel();

// --- 2. EXTRACT 225 FEATURES FROM MEDIAPIPE ---
function extractKeypoints(results) {
    // Extract Pose (33 landmarks * 3 coordinates = 99)
    let pose = new Array(99).fill(0);
    if (results.poseLandmarks) {
        pose = results.poseLandmarks.map(res => [res.x, res.y, res.z]).flat();
    }

    // Extract Left Hand (21 landmarks * 3 coordinates = 63)
    let lh = new Array(63).fill(0);
    if (results.leftHandLandmarks) {
        lh = results.leftHandLandmarks.map(res => [res.x, res.y, res.z]).flat();
    }

    // Extract Right Hand (21 landmarks * 3 coordinates = 63)
    let rh = new Array(63).fill(0);
    if (results.rightHandLandmarks) {
        rh = results.rightHandLandmarks.map(res => [res.x, res.y, res.z]).flat();
    }

    // Combine into a single array of exactly 225 features
    return pose.concat(lh, rh);
}

// --- 3. RUN PREDICTION ---
async function predictSign(landmarkData) {
    if (!model) return;

    // Convert flat array (6750) to 3D Tensor [1, 30, 225]
    const inputTensor = tf.tensor3d(landmarkData, [1, sequenceLength, features]);
    
    const prediction = model.predict(inputTensor);
    const probabilities = await prediction.data();
    const highestIdx = prediction.argMax(-1).dataSync()[0];
    const confidence = probabilities[highestIdx] * 100;

    // Only update if confidence is high enough (stops the spam)
    if (confidence > confidenceThreshold) {
        const predictedAction = actions[highestIdx];
        predictionText.innerText = `${predictedAction} (${confidence.toFixed(1)}%)`;
    } else {
        predictionText.innerText = "Waiting for gesture...";
    }

    inputTensor.dispose();
    prediction.dispose();
}

// --- 4. MEDIAPIPE FRAME PROCESSING ---
function onResults(results) {
    // 4a. Draw the landmarks on the canvas so you can see yourself
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
    
    // Draw Pose and Hands
    drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {color: '#00FF00', lineWidth: 2});
    drawLandmarks(canvasCtx, results.poseLandmarks, {color: '#FF0000', lineWidth: 1});
    drawConnectors(canvasCtx, results.leftHandLandmarks, HAND_CONNECTIONS, {color: '#CC0000', lineWidth: 2});
    drawLandmarks(canvasCtx, results.leftHandLandmarks, {color: '#00FF00', lineWidth: 1});
    drawConnectors(canvasCtx, results.rightHandLandmarks, HAND_CONNECTIONS, {color: '#00CC00', lineWidth: 2});
    drawLandmarks(canvasCtx, results.rightHandLandmarks, {color: '#FF0000', lineWidth: 1});
    canvasCtx.restore();

    // 4b. Extract the math and feed it to the sequence array
    const keypoints = extractKeypoints(results);
    sequence.push(keypoints);

    if (sequence.length > sequenceLength) {
        sequence.shift();
    }

    if (sequence.length === sequenceLength) {
        predictSign(sequence.flat());
    }
}

// --- 5. INITIALIZE WEBCAM & MEDIAPIPE ---
const holistic = new Holistic({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
}});

holistic.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    enableSegmentation: false,
    refineFaceLandmarks: false,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});

holistic.onResults(onResults);

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await holistic.send({image: videoElement});
    },
    width: 640,
    height: 480
});

camera.start();
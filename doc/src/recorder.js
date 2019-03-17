function Microphone(_fft) {
    var FFT_SIZE = _fft || 1024;
    this.spectrum = [];
    this.volume = this.vol = 0;
    this.peak_volume = 0;
    this.mapSound = function (_me, _total, _min, _max) {
        alert(this.volume);
        if (this.spectrum.length > 0) {
            // map to defaults if no values given
            var min = _min || 0;
            var max = _max || 100;
            //actual new freq
            var new_freq = Math.floor(_me * this.spectrum.length / _total);
            // map the volumes to a useful number
            return map(this.spectrum[new_freq], 0, this.peak_volume, min, max);
        } else {
            return 0;
        }
    };
    var self = this;
    var audioContext = new AudioContext();
    var SAMPLE_RATE = audioContext.sampleRate;

    // this is just a browser check to see
    // if it supports AudioContext and getUserMedia
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    // now just wait until the microphone is fired up
    window.addEventListener('load', init, false);
    function init() {
        try {
            startMic(new AudioContext());
        }
        catch (e) {
            console.error(e);
            alert('Web Audio API is not supported in this browser');
        }
    }
    function startMic(context) {
        navigator.getUserMedia({ audio: true }, processSound, error);
        function processSound(stream) {
            // analyser extracts frequency, waveform, etc.
            var analyser = context.createAnalyser();
            analyser.smoothingTimeConstant = 0.2;
            analyser.fftSize = FFT_SIZE;
            var node = context.createScriptProcessor(FFT_SIZE * 2, 1, 1);
            node.onaudioprocess = function () {
                // bitcount returns array which is half the FFT_SIZE
                this.spectrum = new Uint8Array(analyser.frequencyBinCount);
                // getByteFrequencyData returns amplitude for each bin
                analyser.getByteFrequencyData(this.spectrum);
                // getByteTimeDomainData gets volumes over the sample time
                // analyser.getByteTimeDomainData(self.spectrum);

                self.vol = getRMS(this.spectrum);
                // get peak - a hack when our volumes are low
                if (self.vol > self.peak_volume) self.peak_volume = self.vol;
                self.volume = self.vol;
            };
            var input = context.createMediaStreamSource(stream);
            input.connect(analyser);
            analyser.connect(node);
            node.connect(context.destination);
        }
        function error() {
            console.log(arguments);
        }
    }
    //////// SOUND UTILITIES  ////////
    function map(value, min1, max1, min2, max2) {
        var returnvalue = ((value - min1) / (max1 - min1) * (max2 - min2)) + min2;
        return returnvalue;
    };

    function getRMS(spectrum) {
        var rms = 0;
        for (var i = 0; i < spectrum.length; i++) {
            rms += spectrum[i] * spectrum[i];
        }
        rms /= spectrum.length;
        rms = Math.sqrt(rms);
        return rms;
    }

    return this;
};

module.exports.Mic = new Microphone();
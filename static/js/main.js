function startProgress() {
    $('#progress-container').show();
    var interval = setInterval(function() {
        $.get('/progress', function(data) {
            var progress = data.progress;
            $('#progress').css('width', progress + '%');
            if (progress >= 100) {
                clearInterval(interval);
                alert('Processing complete!');
            }
        });
    }, 1000);
}

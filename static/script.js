$(document).ready(function() {
    $("#start-batch").click(function() {
        let mode = $("#mode").val();

        $.ajax({
            url: "/start_batch",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ mode: mode }),
            success: function(response) {
                alert(response.message);
                location.reload();
            }
        });
    });

    $("#complete-batch").click(function() {
        $.ajax({
            url: "/complete_batch",
            type: "POST",
            contentType: "application/json",
            success: function(response) {
                alert(response.message);
                location.reload();
            }
        });
    });
});

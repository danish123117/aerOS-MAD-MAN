$(document).ready(function() {
    $("#start-batch").click(function() {
        let mode = $("#mode").val();

        // Disable Start Batch button and enable Complete Batch button
        $("#start-batch").prop("disabled", true).css("background", "gray");
        $("#complete-batch").prop("disabled", false).css("background", "green");

        $.ajax({
            url: "/start_batch",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ mode: mode }),
            success: function(response) {
                updateUI(response);
            }
        });
    });

    $("#complete-batch").click(function() {
        $.ajax({
            url: "/complete_batch",
            type: "POST",
            contentType: "application/json",
            success: function(response) {
                updateUI(response);
            }
        });
    });

    function updateUI(data) {
        // Update Waiting List
        let waitingListHtml = "";
        data.incompleteOrderList.forEach(order => {
            waitingListHtml += `<tr>
                                    <td>${order[0]}</td>
                                    <td>${order[1]}</td>
                                    <td>${order[2]}</td>
                                </tr>`;
        });
        $("#waiting-list").html(waitingListHtml);
        $("#waiting").text(data.incompleteOrderList.length);

        // Update Current Batch List
        let currentBatchHtml = "";
        data.processingOrderList.forEach(order => {
            currentBatchHtml += `<tr>
                                    <td>${order[0]}</td>
                                    <td>${order[1]}</td>
                                    <td>${order[2]}</td>
                                </tr>`;
        });
        $("#current-batch").html(currentBatchHtml);
        $("#inprocess").text(data.processingOrderList.length);

        // Update Processed Orders Count
        $("#processed").text(data.completedOrderList.length);
    }
});

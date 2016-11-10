$(".take-trip-form").submit(function() {
    var $form = $(this);
    $.ajax({
        url: $form.attr("action") || "",
        type: $form.attr("method") || "GET",
        data: $form.serialize(),
        cache: false
    }).fail(function(xhr) {
        alert("Failed to take trip: " + (xhr.responseText || xhr.statusMessage || "Unknown error"));
    }).done(function(data) {
        $form.closest("tr").addClass("warning");
        $form.replaceWith($("<a>Review</a>").attr("href", "/reviewForm?tripId=" + encodeURIComponent(data)));
    });
    return false;
});

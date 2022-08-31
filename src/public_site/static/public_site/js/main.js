$(document).ready(function () {
  // main page mobile menu toggle
  $(".menu-icon").click(function () {
    $("#mobile-menu").toggleClass("hideMenu");
  });
  //side bar toggle on mobile
  $(".sidebar-button-toggle").click(function () {
    // get this toggle
    const toggle = $(this).data("toggle");
    if (toggle === "graph-toggle") {
      // graph operates indipendetly
      $(this).toggleClass("active");
      $("#" + toggle).toggle();
    } else {
      $(".sidebar-button-toggle").not(".graph-button").removeClass("active");
      $(this).addClass("active");
      //if it's open, close it and make it not active
      if ($("#" + toggle).is(":visible")) {
        $(".control").hide();
        $("#" + toggle).hide();
        $(".sidebar-button-toggle").not(".graph-button").removeClass("active");
      } else {
        // hide the other ones
        $(".control").hide();
        // show the selected
        $("#" + toggle).show();
      }
    }
  });
  // cancel the open thing
  $(document).keyup(function (e) {
    // ...with the esc key
    if (e.keyCode === 27) {
      $(".control").hide();
      $(".sidebar-button-toggle").not(".graph-button").removeClass("active");
      $(".modal").hide();
    }
  });
  $("#map,header,footer,.graph,#date-stepper-wrapper,.graph-button").mousedown(
    function () {
      $(".control").hide();
      $(".sidebar-button-toggle").not(".graph-button").removeClass("active");
    }
  );
  //this changes the legend
  $(".hiiSelector").change(function () {
    if (this.id === "nolayer") {
      $("#legend-wrapper").hide();
    } else {
      $("#legend-wrapper").show();
      $(".legend").removeClass("rainbow purple nolayer").addClass(this.id);
    }
  });
  $(".download-country").click(function () {
    const country = $(this).data("country");
    const iso2 = $(this).data("iso2");
    //show the download modal
    $("#download-modal").css("display", "grid");
    //update the button text and DL location
    $("span.country-name").html(country);

    $(".download-for")
      .off("click")
      .on("click", function () {
        const type = $(this).data("type");
        if (iso2 === "global") {
          window.location.href = `../api/${type}/global`;
        } else {
          window.location.href = `../api/${type}/country/${iso2}`;
        }
        $("#download-modal").hide();
      });
  });

  //show the modals
  $(".country-note").click(function () {
    $("#country-modal").css("display", "grid");
  });
  $(".about-button").click(function () {
    $("#about-modal").css("display", "grid");
  });
  // close the modals
  $(".modal .close").click(function () {
    $("#download-modal, #country-modal, #about-modal").hide();
  });
  // quick filter
  $("#country-filter").keyup(function (e) {
    //not enter
    if (e.keyCode !== 13) {
      let results = 0;
      $("#no-filter-results").hide();
      const searchTerm = $(this).val().trim().toLowerCase();
      $("li.country")
        .hide()
        .each(function () {
          let thisCountry = $(this).data("country-name").toLowerCase();
          if (thisCountry.includes(searchTerm)) {
            results++;
            $(this).css("display", "flex");
          }
        });
      if (results === 0) {
        $("#no-filter-results").show();
      }
    }
  });
  $("#country-filter-form").submit(function (e) {
    $("ul#countries")
      .find("li:visible:first input")
      .attr("checked", true)
      .trigger("change");
    e.preventDefault();
  });
  const path = "/static/public_site/animations/";
  $("button.animation").click(function () {
    // switch the current gif
    const fileName = $(this).data("imgsrc");
    const img = $(".img-animation");
    // make the button active
    $("button.animation").removeClass("active");
    $(this).addClass("active");
    // update the gif
    img.attr("src", `${path}${fileName}.gif`);
    // update the caption
    $("figcaption").html($(this).html());
    // remove the paused overlay
    $("figure").removeClass("paused");
  });
  $("figure").click(function () {
    //play/pause when they click the image
    const currentImg = $(this).find("img");
    const fileName = $("button.animation.active").data("imgsrc");
    if ($(this).hasClass("paused")) {
      $(this).removeClass("paused");
      currentImg.attr("src", `${path}${fileName}.gif`);
    } else {
      $(this).addClass("paused");
      currentImg.attr("src", `${path}${fileName}.png`);
    }
  });
});

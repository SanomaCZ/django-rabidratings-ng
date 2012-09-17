/**
 * RabidRatings - Simple and Pretty Ratings for Everyone
 * JavaScript functionality requires MooTools version 1.2 <http://www.mootools.net>.
 * 
 * Full package available at <http://widgets.rabidlabs.net/ratings>.
 * django version at http://code.google.com/p/djang-rabid-ratings/
 *
 * NOTE: The included JavaScript WILL ONLY WORK WITH MOOTOOLS.  It will not work if any other JavaScript
 * framework is present on the page.
 *
 * Current MooTools version: 1.2
 *
 * @author Michelle Steigerwalt <http://www.msteigerwalt.com>
 * @copyright 2007, 2008 Michelle Steigerwalt, 2008 Darrel Herbst
 * @license LGPL 2.1 <http://creativecommons.org/licenses/LGPL/2.1/>
 */

var RabidRatings = function (options) {
	rr = {
		options: {
			url: null,
			leftMargin: 0,  /* The width in pixels of the margin before the stars. */
			starWidth: 17,  /* The width in pixels of each star. */
			starMargin: 4,  /* The width in pixels between each star. */
			scale: 5,       /* It's a five-star scale. */
			snap: 1,         /* Will snap to the nearest star (can be made a decimal, too). */
			verbalValues: {1: 'Very bad', 2: 'Bad', 3: 'Avarage', 4: 'Good', 5: 'Excellent'} /* verbal values for individual stars*/
		},

		init: function() {
			var activeColor = this.options.activeColor;
			var votedColor  = this.options.votedColor;
			var fillColor   = this.options.fillColor;
			
			$.each($('.rabidRatingStatistics'), $.proxy(function(index, elStatistics) {
				if (($.browser.msie && $.browser.version=="6.0")) {
					//Replaces all the fancy with a text description of the votes for IE6.
					//If you want IE6 users to have something fancier to look at, add it here.
					$('.ratingText', elStatistics).insertBefore(elStatistics);
					$(elStatistics).remove();
				}
				else
				{
					elStatistics.id = $(elStatistics).attr('id');
					elStatistics.fill = $('.ratingFill', elStatistics);
					elStatistics.textEl = $('.ratingText', elStatistics);
					elStatistics.totalVotes = $('.totalVotes', elStatistics.textEl);
					elStatistics.ratingAvg = $('.ratingAvg', elStatistics.textEl);
					elStatistics.starPercent = this.getStarPercentFromId(elStatistics.id);
					this.fillVote(elStatistics.starPercent, elStatistics);
				}
			}, this));

			$.each($('.rabidRatingUser'), $.proxy(function(index, el) {
				if (($.browser.msie && $.browser.version=="6.0")) {
					//Replaces all the fancy with a text description of the votes for IE6.
					//If you want IE6 users to have something fancier to look at, add it here.
					$('.ratingText', el).insertBefore(el);
					$(el).remove();
				}
				else
				{
					//Does this if the browser is NOT IE6. IE6 users don't deserve fancy ratings. >:(
					el.id = $(el).attr('id');
					el.wrapper = $('.wrapper', el);
					el.textEl = $('.ratingText', el);
					el.offset = $(el).offset().left
					el.fill = $('.ratingFill', el);
					el.starPercent = this.getStarPercentFromId(el.id);
					el.ratableId   = this.getRatableId(el.id);
					el.csrf = this.getCsrfProtection();
					this.fillVote(el.starPercent, el);
					
					// used for statistics part
					elStatistics = $('.rabidRatingStatistics')[index]
					if (elStatistics) {
						elStatistics.fill = $('.ratingFill', elStatistics);
						elStatistics.textEl = $('.ratingText', elStatistics);
						elStatistics.totalVotes = $('.totalVotes', elStatistics.textEl);
						elStatistics.ratingAvg = $('.ratingAvg', elStatistics.textEl);
						elStatistics.starPercent = this.getStarPercentFromId(elStatistics.id);
						this.fillVote(elStatistics.starPercent, elStatistics);
					}
					// end used for statistics part
					
					el.currentFill = this.getFillPercent(el.starPercent);

					el.mouseCrap = $.proxy(function(e) {
						var fill = e.pageX - $(el).offset().left;
						if (($.browser.msie && $.browser.version=="7.0")) {
							// damn IE7 - hack - hardcoded position
							var fill = e.pageX - 820;
						}
						var fillPercent = this.getVotePercent(fill);
						var step = (100 / this.options.scale) * this.options.snap;
						var nextStep = Math.floor(fillPercent / step) + 1;
						$(el.textEl).html(this.options.verbalValues[nextStep]);
						this.fillVote(nextStep * step, el);
					}, this);

					el.mouseenter = function(e) {
						el.oldText = $(el.textEl).html();
						$(el).toggleClass('.rabidRatingUser .ratingActive')
						el.wrapper.mousemove(el.mouseCrap)
					}

					el.mouseleave = function(e) {
						$(el).unbind('mousemove', el.mouseCrap);
						$(el).toggleClass('.rabidRatingUser .ratingFill');
						$(el.fill).css('width',el.currentFill);
						$(el.textEl).html(el.oldText);
					}

					el.click = $.proxy(function(e) {
						el.currentFill = el.newFill;
						$(el.fill).toggleClass('.rabidRatingUser .ratingVoted');
						$(el.wrapper).unbind();
						$(el).addClass('ratingVoted');
						$(el.textEl).addClass('loading');
						var votePercent = this.getVotePercent(el.newFill);
						if (this.options.url != null) {
							$.ajax({
								beforeSend: function(xhrObj){
                        			xhrObj.setRequestHeader('X-CSRFToken', el.csrf);
                    			},
                    			url: this.options.url,
								type: 'POST',
								dataType: "json",
								success: el.setResultVaules,
								data: {vote: votePercent,
									   id: el.ratableId,
									   csrf_token: el.csrf,
                        		       csrf_name: 'csrfmiddlewaretoken',
                                       csrf_xname: 'X-CSRFToken',
									   csrfmiddlewaretoken:el.csrf}
							});
						}
					}, this)

					el.wrapper.mouseenter(el.mouseenter);
					el.wrapper.mouseleave(el.mouseleave);
					el.wrapper.click(el.click);

					el.setResultVaules = $.proxy(function(data) {
						if (data.code == 200) {
							$(el.textEl).removeClass('loading');
							$(el.textEl).html(data.text);
							// used for statistics part
							if (elStatistics) {
								$(elStatistics.totalVotes).html(data.total_votes);
								$(elStatistics.ratingAvg).html(data.avg_rating);
								var percent = this.computeStarPercent(data.avg_rating, this.options.scale)
								this.fillVote(percent, elStatistics);
							}
							// end used for statistics part 
						}
						else {
							el.showError(data.error); return false;
						}
					}, this);
					
					el.showError = $.proxy(function(error) {
						$(el.textEl).addClass('ratingError');
						oldTxt = $(el.textEl).html();
						$(el.textEl).html(error);
						$(el).delay(1000).queue($.proxy(function() {
							$(el.textEl).html(oldTxt);
							$(el.textEl).removeClass('ratingError');
							el.wrapper.mouseenter(el.mouseenter);
							el.wrapper.mouseleave(el.mouseleave);
							el.wrapper.click(el.click);
							this.fillVote(el.starPercent, el);
							if (elStatistics) this.fillVote(elStatistics.starPercent, elStatistics);
						}, this));
					}, this);
				}
			}, this));
		},

		fillVote: function(percent, el) {
			el.newFill = this.getFillPercent(percent);
			if (this.getVotePercent(el.newFill) > 100) { el.newFill = this.getFillPercent(100); }
			el.fill.css('width', el.newFill);
		},

		getStarPercentFromId: function(id) {
			/* Format = anyStringHere-<id>-<float(currentStars)>_(scale); 
			 * Example: rabidRatingUser-5_5-3_5 //Primary key id = 5, 3/5 stars. */
			var stars = id.match(/([^-]+)-(\d*\.?\d+)_(\d*\.?\d+)$/);
			var ratableId = parseFloat(stars[1]);
			return this.computeStarPercent(stars[2], stars[3]);
		},
		
		computeStarPercent: function(score, scale) {
			var percent =  (parseFloat(score) / parseFloat(scale)) * 100;
			return percent;
		},

		getFillPercent: function (starPercent) {
			return (starPercent/100)*((this.options.starWidth+this.options.starMargin)*this.options.scale) + this.options.leftMargin;
		},

		getVotePercent: function(divPosition) {
			var starsWidth = (this.options.starWidth+this.options.starMargin)*this.options.scale;
			var offset = this.options.leftMargin;
			var starPosition = divPosition - this.options.leftMargin;
			var percent = (starPosition / starsWidth * 100).toFixed(2);
			return percent;
		},

		getRatableId: function(id) {
			var stars = id.match(/([^-]+)-(\d*\.?\d+)_(\d*\.?\d+)$/);
			return stars[1];
		},
				
		getCsrfProtection: function() {
			var csrftoken = $.cookie('csrftoken');
			return csrftoken;
		}
	}
	$.extend(rr.options, options)
	rr.init()
	return rr
}

$(document).ready(function(e) {
	var rating = new RabidRatings({url:rabidratings_submit_url,
								   verbalValues:rabidratings_verbal_values
		});
});

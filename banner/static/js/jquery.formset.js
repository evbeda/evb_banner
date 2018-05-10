;(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),

            button_search = document.getElementsByClassName("evb_id_button")
            flatExtraClasses = options.extraClasses.join(' '),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
            childElementSelector = 'input,select,textarea,label,div',
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find(childElementSelector).length > 0;
            },

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                if (del.is(':checked')) {
                    // If an inline formset containing deleted forms fails validation, make sure
                    // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                }
                // Hide any labels associated with the DELETE checkbox:
                $('label[for="' + del.attr('id') + '"]').hide();
                del.remove();
            }
            if (hasChildElements(row)) {
                row.addClass(options.formCssClass);
                if (row.is(':visible')) {
                    applyExtraClasses(row, i);
                }
            }
        });

        if ($$.length) {
            if (options.formTemplate) {
                // If a form template was specified, we'll clone it to generate new form instances:
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass + ' formset-custom-template');
                template.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, '__prefix__');
                });
            } else {
                // Otherwise, use the last form in the formset; this works much better if you've got
                // extra (>= 1) forms (thnaks to justhamade for pointing this out):
                template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
                template.find('input:hidden[id $= "-DELETE"]').remove();
                // Clear all cloned fields, except those the user wants to keep (thanks to brunogola for the suggestion):
                template.find(childElementSelector).not(options.keepFieldValues).each(function() {
                    var elem = $(this);
                    // If this is a checkbox or radiobutton, uncheck it.
                    // This fixes Issue 1, reported by Wilson.Andrew.J:
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.attr('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }
            // FIXME: Perhaps using $.data would be a better idea?
            options.formTemplate = template;

            $(".evb_id_button").click(function() {
                var evb_id_search = $(".evb_id_input").val();
                var formCount = parseInt(totalForms.val());
                var xhttp = new XMLHttpRequest();
                document.getElementsByClassName("loader")[0].classList.remove('d-none')
                    xhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 500) {
                            debugger
                            document.getElementsByClassName("error_label")[0].classList.remove('d-none')
                            document.getElementsByClassName("loader")[0].classList.add('d-none')
                        }
                        if (this.readyState == 4 && this.status == 200) {
                            event = JSON.parse(this.responseText);
                                row = options.formTemplate.clone(true),
                                delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, '.');
                            applyExtraClasses(row, formCount);
                            forms = document.getElementsByClassName("event-formset")
                            last_form = forms[forms.length - 1]
                            row.insertAfter(last_form).show();
                            row.find(childElementSelector).each(function() {
                                updateElementIndex($(this), options.prefix, formCount);
                            });
                            totalForms.val(formCount + 1);

                            row.find(childElementSelector)[5].getElementsByClassName("js-event-card-title")[0].innerHTML = event['title']
                            row.find(childElementSelector)[6].getElementsByClassName("description")[0].innerHTML = event['description']
                            row.find(childElementSelector)[4].getElementsByClassName("image")[0].setAttribute('src', event['logo'])
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-title").value = event['title']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-description").value = event['description']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-logo").value = event['logo']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-start").value = event['start']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-end").value = event['end']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-organizer").value = event['organizer']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-evb_id").value = event['evb_id']
                            document.getElementById("id_form-"+(totalForms.val()-1)+"-evb_url").value = event['evb_url']
                            document.getElementsByClassName("loader")[0].classList.add('d-none')
                        }
                    };
                    xhttp.open("POST", "/banner/new/id", true);
                    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                    xhttp.send("id="+evb_id_search);

                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        deleteText: 'remove',            // Text for the delete link
        addCssClass: 'add-row',          // CSS class applied to the add link
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        keepFieldValues: '',             // jQuery selector for fields whose values should be kept when the form is cloned
        added: null,                     // Function called each time a new form is added
        removed: null                    // Function called each time a form is deleted
    };
})(jQuery);
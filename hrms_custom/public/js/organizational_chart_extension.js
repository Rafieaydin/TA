frappe.pages['organizational-chart'].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Organizational Chart',
		single_column: true
	});

	let page = wrapper.page;
	let organizational_chart;
	let current_view = ''; // default view

	// Setup page styling
	page.main.addClass("frappe-card");
	page.main.css({
		"min-height": "300px",
		"max-height": "700px",
		overflow: "auto",
		position: "relative"
	});


	// Inject custom CSS untuk warna node dan connector
	if (!$('#custom-org-chart-colors').length) {
		$('<style id="custom-org-chart-colors">')
			.text(`
				/* Node Card Colors */
				.node-card {
					background: linear-gradient(135deg, #1f305e 0%, #2c4484 100%) !important;
					border: none !important;
					box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4) !important;
				}

					.node-card .node-name,
						.node-name.d-flex, .node-name.d-flex.flex-row {
							display: flex !important;
							align-items: center !important;
							gap: 14px !important; /* increased gap between text and edit button */
						}
				.node-card .node-title {
					color: white !important;
				}

				.node-meta .mr-3 {
					display: none !important;
				}

				.node-name {
					align-items: center;
					justify-content: space-between;
					margin-bottom: 2px;
					width: 20rem;
				}

				.node-name span.ellipsis {
					font-size: 12px;
						color: #ffffff !important; /* make ellipsis text white for contrast */

				}

				.node-card.active {
					background: linear-gradient(135deg, #E34234 0%, #cc3b2f 100%) !important;
					box-shadow: 0 6px 12px rgba(245, 87, 108, 0.5) !important;
					transform: scale(1.05);
				}

				.node-card.active .node-name {
						width: 16rem;
				}

				.node-card.active-path {
					background: linear-gradient(135deg, #1f305e 0%, #2c4484 100%) !important;
					box-shadow: 0 4px 8px rgba(79, 172, 254, 0.4) !important;
				}

				.node-card.collapsed {
					background: linear-gradient(135deg, #1f305e 0%, #2c4484 100%) !important;
					opacity: 0.7;
				}

				/* Connector Colors */
				.active-connector {
					stroke: #E34234 !important;
					stroke-width: 3px !important;
				}

				.collapsed-connector {
					stroke: #1f305e !important;
					stroke-width: 2px !important;
				}

				/* Connections Badge */
				.node-card .node-connections {
					background: rgba(255, 255, 255, 0.3) !important;
					color: white !important;
					padding: 3px 10px !important;
					border-radius: 12px !important;
					font-weight: 600 !important;
					font-size: 11px !important;
					display: inline-block !important;
					backdrop-filter: blur(10px) !important;
					border: 1px solid rgba(255, 255, 255, 0.5) !important;
				}

				/* Avatar Border */
				.node-card .avatar-frame {
					border: 3px solid white !important;
					box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
				}

				/* Hover Effect */
				.node-card:hover {
					transform: translateY(-2px);
					box-shadow: 0 6px 12px rgba(102, 126, 234, 0.6) !important;
					transition: all 0.3s ease;
				}

					/* If node-name uses flex row with an ellipsis span and an edit button,
					   make the text span flexible so it grows and wraps instead of truncating */
					.node-name.d-flex, .node-name.d-flex.flex-row {
						display: flex !important;
						align-items: center !important;
						gap: 15px !important;
					}

					.node-name.d-flex .ellipsis,
					.node-name .ellipsis {
						flex: 1 1 320px !important;     /* allow to grow/shrink, start wider */
						max-width: 200px !important;          /* allow proper flex shrinking */
						white-space: normal !important;  /* allow wrapping */
						word-break: break-word !important;
						overflow-wrap: anywhere !important;
						overflow: visible !important;
						text-overflow: clip !important;
					}

					/* Keep edit button fixed size so text gets the remaining space */
					.node-name .btn-edit-node,
					.node-name .node-edit-icon,
					.node-name .edit-chart-node {
						flex: 0 0 auto !important;
						margin-left: 2px !important; /* more breathing room */
					}

					/* Flexible nodes: allow wrapping for long text and reasonable sizing */
					.hierarchy-chart .node-card,
					.node-card {
						display: inline-flex !important;
						flex-direction: column !important;
						vertical-align: top;
						min-width: 120px !important;
						max-width: 520px !important; /* increased to allow wider nodes */
						white-space: normal !important;
						word-break: break-word !important;
						overflow-wrap: anywhere !important;
						box-sizing: border-box !important;
					}

					/* Ensure inner text elements wrap and don't ellipsize */
					.hierarchy-chart .node-card .node-name,
					.hierarchy-chart .node-card .node-title,
					.node-card .node-content,
					.node-card .node-meta {
						white-space: normal !important;
						overflow: visible !important;
						text-overflow: unset !important;
						word-break: break-word !important;
						overflow-wrap: anywhere !important;
						display: block !important;
						max-height: none !important;
						height: auto !important;
					}

					/* Flex children should be allowed to shrink so text can wrap */
					.node-card .node-row,
					.node-card .node-info {
						flex: 1 1 auto !important;
						min-width: 0 !important;
					}

					/* Limit avatar size so text gets space */
					.node-card .avatar-frame {
						flex: 0 0 auto !important;
						margin-right: 8px;
						max-width: 64px !important;
					}

					/* Ensure node container doesn't clip its content */
					.node-card {
						height: auto !important;
						overflow: visible !important;
					}
			`)
			.appendTo('head');
	}

	// Custom company selector
	let selected_company = frappe.defaults.get_default("company");
	let selected_department = frappe.defaults.get_default("department");
	format = (selected_company != null ? selected_company : '') + (selected_department != null ? ' - ' + selected_department : '');

	let company_selector_html = `
		<div class="custom-company-selector" style="padding: 10px 15px; border-bottom: 1px solid #d1d8dd; background: #f9fafb; position: relative; z-index: 3;">
			<div style="display: flex; align-items: center; gap: 10px;">
				<strong style="font-size: 14px; color: #1f2937;">Company:</strong>
				<div class="company-display" style="flex: 1; padding: 7px 12px; background: white; border: 1px solid #d1d8dd; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s; position: relative; z-index: 1001;">
					<span class="company-name" style="color: #374151; font-size: 14px;">${format || 'Click to select company'}</span>
					<svg style="width: 16px; height: 16px; color: #6b7280;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
					</svg>
				</div>
			</div>
		</div>
	`;

	page.main.prepend(company_selector_html);

	// Click handler - menggunakan event delegation pada page.main
	page.main.on('click', '.company-display', function () {
		let dialog = new frappe.ui.Dialog({
			title: __('Select Company'),
			fields: [{
				fieldtype: 'Link',
				fieldname: 'company',
				label: __('Company'),
				options: 'Company',
				default: selected_company,
				reqd: 1,
				onchange: function () {
					// Clear department field when company changes
					dialog.set_value('department', '');
					// Refresh department field to apply new filter
					if (dialog.fields_dict.department) {
						dialog.fields_dict.department.refresh();
					}
				}
			},
			{
				fieldtype: 'Check',
				fieldname: 'has_department',
				label: __('Filter by Department'),
				onchange: function () {
					let has_dept = dialog.get_value('has_department');
					if (has_dept) {
						dialog.set_df_property('department', 'reqd', 1);
						dialog.get_field('department').$wrapper.show();
					} else {
						dialog.set_df_property('department', 'reqd', 0);
						dialog.set_value('department', '');
						dialog.get_field('department').$wrapper.hide();
					}
				}
			},
			{
				fieldtype: 'Link',
				fieldname: 'department',
				label: __('Department'),
				options: 'Department',
				depends_on: 'eval:doc.has_department',
				get_query: function () {
					let company = dialog.get_value('company');
					if (company) {
						return {
							filters: {
								'company': company
							}
						};
					}
					return {};
				}
			}
			],
			primary_action_label: __('Select'),
			primary_action: function (values) {
				selected_company = values.company;
				selected_department = values.department;
				current_view = 'department';
				$('.company-name').text(selected_company + (selected_department ? ' - ' + selected_department : ''));
				loadChart(current_view, selected_company, selected_department);
				dialog.hide();
			}
		});
		dialog.show();
	});

	// Hover effect - menggunakan event delegation pada page.main
	page.main.on('mouseenter', '.company-display', function () {
		$(this).css({
			'border-color': '#3b82f6',
			'box-shadow': '0 0 0 3px rgba(59, 130, 246, 0.1)'
		});
	}).on('mouseleave', '.company-display', function () {
		$(this).css({
			'border-color': '#d1d8dd',
			'box-shadow': 'none'
		});
	});

	// View toggle buttons in toolbar
	page.add_inner_button(__('Departments'), function () {
		current_view = 'department';
		if (selected_company) {
			loadChart('department', selected_company);
		} else {
			frappe.msgprint(__('Please select a company first'));
		}
	}, __('View'));

	page.add_inner_button(__('Employees'), function () {
		current_view = 'employee';
		if (selected_company) {
			loadChart('employee', selected_company);
		} else {
			frappe.msgprint(__('Please select a company first'));
		}
	}, __('View'));

	// Add view indicator label after page loads
	setTimeout(() => {
		//let view_indicator = $('<div class="view-indicator" style="display: inline-block; margin-left: 10px; padding: 6px 14px; background: #48bb78; color: white; border-radius: 5px; font-size: 13px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>');
		let view_indicator = $('<div class="view-indicator" style="font-weight:bold;"></div>');

		page.set_title_sub = function (subtitle) {
			view_indicator.text(subtitle);
		};

		// Append to page title area
		$('.title-area>div>.flex').append(view_indicator);

		// Initial text ganti jadi kosong
		view_indicator.text(__(''));
	}, 300);

	function updateViewIndicator(view) {
		if (view === 'department') {
			page.set_title_sub(__('| Departments'));
			// $('.view-indicator').css('background', '#667eea');
		} else if (view === 'employee') {
			page.set_title_sub(__('| Employees'));
			// $('.view-indicator').css('background', '#48bb78');
		} else {
			page.set_title_sub('');
		}
	}
	// Function to hide avatar in department view
	function hideAvatar(view) {
		if (view === 'department') {
			$('.node-card .node-meta .mr-3').hide();
		} else {
			$('.node-card .node-meta .mr-3').show();
		}

	}
	// Function to load chart
	function loadChart(view, company, department) {
		// Update view indicator
		updateViewIndicator(view);

		frappe.require("hierarchy-chart.bundle.js", () => {
			// Clear existing chart
			page.main.find('#hierarchy-chart-wrapper').remove();

			let method;
			let doctype;

			if (view === 'department') {
				method = 'hrms_custom.api.get_department_children';
				doctype = 'Department';
			} else {
				method = 'hrms_custom.api.get_employee_children';
				doctype = 'Employee';
			}
			hideAvatar(view); // Hide or show avatar based on view

			// Create chart
			if (frappe.is_mobile()) {
				organizational_chart = new hrms.HierarchyChartMobile(doctype, wrapper, method);
			} else {
				organizational_chart = new hrms.HierarchyChart(doctype, wrapper, method);
			}

			// Override company to use selected one
			organizational_chart.company = [company, department];

			// Render chart
			organizational_chart.make_svg_markers();
			organizational_chart.setup_hierarchy();
			organizational_chart.render_root_nodes();

			// Override load_children to trigger event after loading
			let original_load_children = organizational_chart.load_children.bind(organizational_chart);
			organizational_chart.load_children = function (node, deep = false) {
				original_load_children(node, deep);
			};

			// Setup click handlers for nodes
			setTimeout(() => {
				setupNodeClickHandlers(organizational_chart, doctype);
			}, 500);

			// Setup Export and Expand buttons
			page.clear_inner_toolbar();

			// Re-add view buttons
			page.add_inner_button(__('Departments'), function () {
				loadChart('department', company, department);
			}, __('View'));

			page.add_inner_button(__('Employees'), function () {
				loadChart('employee', company, department);
			}, __('View'));

			// Add expand/collapse
			page.add_inner_button(__("Expand All"), function () {
				organizational_chart.load_children(organizational_chart.root_node, true);
				organizational_chart.all_nodes_expanded = true;

				page.remove_inner_button(__("Expand All"));
				page.add_inner_button(__("Collapse All"), function () {
					loadChart(view, company, department);
					organizational_chart.all_nodes_expanded = false;
					page.remove_inner_button(__("Collapse All"));
				});
			});

			// Add export
			page.add_inner_button(__("Export"), function () {
				organizational_chart.export_chart();
			});
		});
	}

	// Auto-trigger on load
	setTimeout(() => {
		if (selected_company) {
			loadChart(current_view, selected_company);
		}
		updateViewIndicator(current_view); // Set initial indicator
	}, 100);

	frappe.breadcrumbs.add("HR");
};

// Setup node click handlers
function setupNodeClickHandlers(organizational_chart, doctype) {
	$('.node-card').off('dblclick').each(function () {
		let $card = $(this);
		let node_id = $card.attr('id');

		if (!node_id) return;

		// Double click - open detail form
		$card.on('dblclick', function (e) {
			e.preventDefault();
			e.stopPropagation();
			frappe.set_route('Form', doctype, node_id);
		});
	});

	// Re-attach expand/collapse handlers after children load
	$(document).off('hierarchy-children-loaded').on('hierarchy-children-loaded', function () {
		setTimeout(() => {
			setupNodeClickHandlers(organizational_chart, doctype);
		}, 100);
	});
}
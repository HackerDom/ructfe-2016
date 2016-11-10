% rebase('base.tpl', title='')

<table id="report-props-table" class="table">
	<tr>
		<td>Crash guid</td>
		<td id="crash_guid"></td>
	</tr>
	<tr>
		<td>Crash reason</td>
		<td id="crash_reason"></td>
	</tr>
	<tr>
		<td>Crash address</td>
		<td id="crash_address"></td>
	</tr>
	<tr>
		<td>Remote IP</td>
		<td id="remote_ip"></td>
	</tr>
</table>

<a id="load-crash" class="btn btn-default btn-lg" href="#" role="button">Download</a>

<h3>Crash thread stack</h3>
<table id="crash-thread-stack-table" class="table">
	<tr>
		<th>Idx</th>
		<th>Module</th>
		<th>Signature</th>
		<th>Source</th>
		<th>Line</th>
	</tr>
</table>

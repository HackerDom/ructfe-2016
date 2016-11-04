% rebase('base.tpl', title='')

<table id="report-props-table">
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
</table>

<h3>Crash thread stack</h3>
<table id="crash-thread-stack-table">
	<tr>
		<th>Idx</th>
		<th>Module</th>
		<th>Signature</th>
		<th>Source</th>
		<th>Line</th>
	</tr>
</table>

<script>
	loadCrash();
</script>
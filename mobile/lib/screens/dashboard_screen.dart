import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/status_badge.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _summary;
  Map<String, dynamic>? _errors;
  bool _loading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _errorMessage = null;
    });
    final api = context.read<AuthProvider>().apiService;
    try {
      final results = await Future.wait([
        api.getDashboardSummary(),
        api.getAnomalyReport(),
      ]);
      if (mounted) {
        setState(() {
          _summary = results[0];
          _errors = results[1];
        });
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _handleLogout() async {
    await context.read<AuthProvider>().logout();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = context.read<AuthProvider>().user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.list_alt),
            tooltip: 'ISO Drawings',
            onPressed: () => context.push('/iso'),
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
            onPressed: () => context.push('/settings'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: _handleLogout,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: _loading && _summary == null
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null && _summary == null
                ? _buildErrorState(theme)
                : _buildContent(theme, user),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/scan'),
        icon: const Icon(Icons.camera_alt),
        label: const Text('Scan'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
    );
  }

  Widget _buildErrorState(ThemeData theme) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline,
                  size: 64, color: theme.colorScheme.error),
              const SizedBox(height: 16),
              Text(
                _errorMessage ?? 'Unknown error',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyLarge,
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildContent(ThemeData theme, Map<String, dynamic>? user) {
    final totalIsos = _summary?['total_isos'] ?? 0;
    final totalLines = _summary?['total_lines'] ?? 0;
    final totalValidations = _summary?['total_validations'] ?? 0;
    final passRate = (_summary?['pass_rate'] ?? 0.0).toDouble();
    final recentErrors = _errors?['errors'] as List<dynamic>? ?? [];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Welcome card
        if (user != null) ...[
          Card(
            color: theme.colorScheme.primaryContainer,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: theme.colorScheme.primary,
                    child: Text(
                      (user['username'] as String? ?? 'U')[0].toUpperCase(),
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Welcome, ${user['username']}',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.onPrimaryContainer,
                          ),
                        ),
                        Text(
                          'Role: ${user['role'] ?? 'user'}',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onPrimaryContainer,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Stats grid
        Text(
          'Overview',
          style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: [
            StatCard(
              title: 'Total ISOs',
              value: totalIsos.toString(),
              icon: Icons.folder_copy,
              color: const Color(0xFF1565C0),
            ),
            StatCard(
              title: 'Total Lines',
              value: totalLines.toString(),
              icon: Icons.linear_scale,
              color: const Color(0xFF2E7D32),
            ),
            StatCard(
              title: 'Validations',
              value: totalValidations.toString(),
              icon: Icons.check_circle_outline,
              color: const Color(0xFF6A1B9A),
            ),
            StatCard(
              title: 'Pass Rate',
              value: '${passRate.toStringAsFixed(1)}%',
              icon: Icons.percent,
              color: passRate >= 80
                  ? const Color(0xFF2E7D32)
                  : passRate >= 50
                      ? const Color(0xFFE65100)
                      : const Color(0xFFC62828),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Pass rate progress bar
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Pass Rate',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '${passRate.toStringAsFixed(1)}%',
                      style: theme.textTheme.titleSmall?.copyWith(
                        color: passRate >= 80
                            ? Colors.green
                            : passRate >= 50
                                ? Colors.orange
                                : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: passRate / 100,
                    minHeight: 12,
                    backgroundColor: theme.colorScheme.surfaceVariant,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      passRate >= 80
                          ? Colors.green
                          : passRate >= 50
                              ? Colors.orange
                              : Colors.red,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Recent errors
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Issues',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            if (_loading)
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
          ],
        ),
        const SizedBox(height: 12),

        if (recentErrors.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  Icon(Icons.check_circle,
                      size: 48, color: Colors.green.shade400),
                  const SizedBox(height: 8),
                  Text(
                    'No recent issues',
                    style: theme.textTheme.bodyLarge,
                  ),
                ],
              ),
            ),
          )
        else
          ...recentErrors.take(10).map((error) {
            final e = error as Map<String, dynamic>;
            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: const Icon(Icons.warning_amber, color: Colors.orange),
                title: Text(
                  e['line_number']?.toString() ??
                      e['filename']?.toString() ??
                      'Unknown',
                  style: theme.textTheme.bodyMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  e['message']?.toString() ??
                      e['error']?.toString() ??
                      'Validation issue',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                trailing: StatusBadge(
                  status: e['status']?.toString() ?? 'error',
                ),
              ),
            );
          }),
      ],
    );
  }
}

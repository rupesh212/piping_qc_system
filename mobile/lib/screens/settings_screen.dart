import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../providers/auth_provider.dart';
import '../services/api_service.dart';

const _appVersion = '1.0.0+1';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _apiUrlController = TextEditingController();
  bool _savingUrl = false;
  bool _testingConnection = false;
  String? _connectionStatus;
  bool? _connectionSuccess;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('api_url') ?? 'http://10.0.2.2:8000';
    if (mounted) setState(() => _apiUrlController.text = saved);
  }

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }

  Future<void> _saveApiUrl() async {
    final url = _apiUrlController.text.trim();
    if (url.isEmpty) return;

    setState(() => _savingUrl = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('api_url', url);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('API URL saved successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _savingUrl = false);
    }
  }

  Future<void> _testConnection() async {
    final url = _apiUrlController.text.trim();
    if (url.isEmpty) return;

    setState(() {
      _testingConnection = true;
      _connectionStatus = null;
      _connectionSuccess = null;
    });

    final tempApi = ApiService(baseUrl: url);
    try {
      final health = await tempApi.checkHealth();
      if (mounted) {
        setState(() {
          _connectionSuccess = true;
          _connectionStatus =
              'Connected! Status: ${health['status'] ?? 'ok'}';
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _connectionSuccess = false;
          _connectionStatus = 'Failed: ${e.message}';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _connectionSuccess = false;
          _connectionStatus = 'Error: $e';
        });
      }
    } finally {
      if (mounted) setState(() => _testingConnection = false);
    }
  }

  Future<void> _handleLogout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirm Logout'),
        content: const Text('Are you sure you want to sign out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Logout'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      await context.read<AuthProvider>().logout();
      if (mounted) context.go('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = context.watch<AuthProvider>().user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // User info card
          if (user != null) ...[
            Text(
              'Account',
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.primary,
                  child: Text(
                    (user['username'] as String? ?? 'U')[0].toUpperCase(),
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
                title: Text(user['username']?.toString() ?? 'Unknown'),
                subtitle: Text('Role: ${user['role']?.toString() ?? 'user'}'),
                trailing: const Icon(Icons.account_circle_outlined),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // API URL
          Text(
            'Connection',
            style: theme.textTheme.titleMedium
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: _apiUrlController,
                    decoration: const InputDecoration(
                      labelText: 'API Base URL',
                      hintText: 'http://10.0.2.2:8000',
                      prefixIcon: Icon(Icons.link),
                    ),
                    keyboardType: TextInputType.url,
                    autocorrect: false,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed:
                              _testingConnection ? null : _testConnection,
                          icon: _testingConnection
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2),
                                )
                              : const Icon(Icons.wifi_tethering),
                          label: const Text('Test Connection'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _savingUrl ? null : _saveApiUrl,
                          icon: _savingUrl
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              : const Icon(Icons.save),
                          label: const Text('Save'),
                        ),
                      ),
                    ],
                  ),
                  if (_connectionStatus != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _connectionSuccess == true
                            ? Colors.green.shade50
                            : Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: _connectionSuccess == true
                              ? Colors.green
                              : Colors.red,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _connectionSuccess == true
                                ? Icons.check_circle
                                : Icons.error_outline,
                            color: _connectionSuccess == true
                                ? Colors.green.shade700
                                : Colors.red.shade700,
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _connectionStatus!,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: _connectionSuccess == true
                                    ? Colors.green.shade800
                                    : Colors.red.shade800,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // App info
          Text(
            'About',
            style: theme.textTheme.titleMedium
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('App Version'),
                  trailing: Text(
                    _appVersion,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                const Divider(height: 1, indent: 16, endIndent: 16),
                ListTile(
                  leading: const Icon(Icons.plumbing),
                  title: const Text('Piping QA/QC System'),
                  subtitle: const Text('Mobile Client'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),

          // Logout button
          SizedBox(
            height: 52,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.error,
                foregroundColor: theme.colorScheme.onError,
              ),
              onPressed: _handleLogout,
              icon: const Icon(Icons.logout),
              label: const Text(
                'Sign Out',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}

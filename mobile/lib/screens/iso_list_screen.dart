import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/status_badge.dart';

class IsoListScreen extends StatefulWidget {
  const IsoListScreen({super.key});

  @override
  State<IsoListScreen> createState() => _IsoListScreenState();
}

class _IsoListScreenState extends State<IsoListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  List<Map<String, dynamic>> _items = [];
  int _skip = 0;
  static const int _limit = 20;
  bool _loading = false;
  bool _loadingMore = false;
  bool _hasMore = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData(refresh: true);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadData({bool refresh = false}) async {
    if (_loading) return;
    if (refresh) {
      _skip = 0;
      _hasMore = true;
    }

    setState(() {
      _loading = refresh;
      _loadingMore = !refresh;
      _errorMessage = null;
    });

    final api = context.read<AuthProvider>().apiService;
    try {
      final search = _searchController.text.trim();
      final result = await api.getISOList(
        skip: _skip,
        limit: _limit,
        search: search.isNotEmpty ? search : null,
      );

      final items = (result['items'] as List<dynamic>? ?? [])
          .cast<Map<String, dynamic>>();

      if (mounted) {
        setState(() {
          if (refresh) {
            _items = items;
          } else {
            _items.addAll(items);
          }
          _skip = _items.length;
          _hasMore = items.length == _limit;
        });
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
          _loadingMore = false;
        });
      }
    }
  }

  void _onSearchChanged(String _) {
    _loadData(refresh: true);
  }

  void _showDetails(Map<String, dynamic> iso) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _IsoDetailSheet(iso: iso),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ISO Drawings'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(64),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
            child: TextField(
              controller: _searchController,
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: 'Search by filename, line number…',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _loadData(refresh: true);
                        },
                      )
                    : null,
                filled: true,
                fillColor: theme.colorScheme.surface,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => _loadData(refresh: true),
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null && _items.isEmpty
                ? _buildError(theme)
                : _buildList(theme),
      ),
    );
  }

  Widget _buildError(ThemeData theme) {
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Center(
          child: Column(
            children: [
              Icon(Icons.error_outline,
                  size: 64, color: theme.colorScheme.error),
              const SizedBox(height: 16),
              Text(_errorMessage ?? 'Unknown error',
                  textAlign: TextAlign.center),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: () => _loadData(refresh: true),
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildList(ThemeData theme) {
    if (_items.isEmpty) {
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Center(
            child: Column(
              children: [
                Icon(Icons.folder_open,
                    size: 64, color: theme.colorScheme.outline),
                const SizedBox(height: 16),
                const Text('No ISO drawings found.'),
              ],
            ),
          ),
        ],
      );
    }

    return ListView.separated(
      controller: _scrollController,
      padding: const EdgeInsets.all(12),
      itemCount: _items.length + (_hasMore ? 1 : 0),
      separatorBuilder: (_, __) => const SizedBox(height: 4),
      itemBuilder: (context, index) {
        if (index >= _items.length) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Center(
              child: _loadingMore
                  ? const CircularProgressIndicator()
                  : ElevatedButton.icon(
                      onPressed: () => _loadData(refresh: false),
                      icon: const Icon(Icons.expand_more),
                      label: const Text('Load More'),
                    ),
            ),
          );
        }
        final iso = _items[index];
        return _IsoCard(iso: iso, onTap: () => _showDetails(iso));
      },
    );
  }
}

class _IsoCard extends StatelessWidget {
  const _IsoCard({required this.iso, required this.onTap});

  final Map<String, dynamic> iso;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final filename = iso['filename']?.toString() ?? 'Unknown';
    final lineNumber = iso['line_number']?.toString() ?? '-';
    final pipeSize = iso['pipe_size']?.toString() ?? '-';
    final spec = iso['spec']?.toString() ?? '-';
    final status = iso['status']?.toString() ?? 'pending';

    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      filename,
                      style: theme.textTheme.titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  StatusBadge(status: status),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 16,
                runSpacing: 4,
                children: [
                  _InfoChip(label: 'Line', value: lineNumber),
                  _InfoChip(label: 'Size', value: pipeSize),
                  _InfoChip(label: 'Spec', value: spec),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label: ',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.bodySmall
              ?.copyWith(fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}

class _IsoDetailSheet extends StatefulWidget {
  const _IsoDetailSheet({required this.iso});

  final Map<String, dynamic> iso;

  @override
  State<_IsoDetailSheet> createState() => _IsoDetailSheetState();
}

class _IsoDetailSheetState extends State<_IsoDetailSheet> {
  bool _validating = false;
  Map<String, dynamic>? _validationResult;
  String? _validationError;

  Future<void> _runValidation() async {
    final isoId = widget.iso['id']?.toString();
    if (isoId == null) return;

    setState(() {
      _validating = true;
      _validationError = null;
    });

    final api = context.read<AuthProvider>().apiService;
    try {
      final result = await api.validateISO(isoId);
      if (mounted) setState(() => _validationResult = result);
    } on ApiException catch (e) {
      if (mounted) setState(() => _validationError = e.message);
    } catch (e) {
      if (mounted) setState(() => _validationError = e.toString());
    } finally {
      if (mounted) setState(() => _validating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final iso = widget.iso;
    final rules = _validationResult?['rules'] as List<dynamic>? ?? [];

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.6,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      builder: (_, scrollController) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: ListView(
          controller: scrollController,
          children: [
            const SizedBox(height: 8),
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: theme.colorScheme.outline,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              iso['filename']?.toString() ?? 'ISO Details',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            StatusBadge(status: iso['status']?.toString() ?? 'pending'),
            const SizedBox(height: 16),

            // Fields
            _DetailRow('Line Number', iso['line_number']?.toString() ?? '-'),
            _DetailRow('Pipe Size', iso['pipe_size']?.toString() ?? '-'),
            _DetailRow('Spec', iso['spec']?.toString() ?? '-'),
            _DetailRow('Weld Count', iso['weld_count']?.toString() ?? '-'),
            _DetailRow('Uploaded', iso['created_at']?.toString() ?? '-'),

            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _validating ? null : _runValidation,
                icon: _validating
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child:
                            CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.verified),
                label: const Text('Run Validation'),
              ),
            ),

            if (_validationError != null) ...[
              const SizedBox(height: 12),
              Text(_validationError!,
                  style: TextStyle(color: theme.colorScheme.error)),
            ],

            if (_validationResult != null) ...[
              const SizedBox(height: 16),
              Text(
                'Validation Results',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...rules.map((rule) {
                final r = rule as Map<String, dynamic>;
                final passed = r['passed'] == true || r['result'] == 'pass';
                return Card(
                  margin: const EdgeInsets.only(bottom: 6),
                  color: passed
                      ? Colors.green.shade50
                      : Colors.red.shade50,
                  child: ListTile(
                    dense: true,
                    leading: Icon(
                      passed ? Icons.check_circle : Icons.cancel,
                      color: passed ? Colors.green : Colors.red,
                    ),
                    title: Text(r['rule']?.toString() ??
                        r['name']?.toString() ??
                        'Rule'),
                    subtitle: r['message'] != null
                        ? Text(r['message'].toString())
                        : null,
                    trailing: StatusBadge(
                        status: passed ? 'pass' : 'fail'),
                  ),
                );
              }),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: theme.textTheme.bodyMedium
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

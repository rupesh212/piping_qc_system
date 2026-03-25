import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/status_badge.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _picker = ImagePicker();

  File? _selectedFile;
  bool _uploading = false;
  bool _validating = false;
  Map<String, dynamic>? _uploadResult;
  Map<String, dynamic>? _validationResult;
  String? _errorMessage;
  double _uploadProgress = 0;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        imageQuality: 90,
        maxWidth: 2400,
        maxHeight: 2400,
      );
      if (picked != null) {
        setState(() {
          _selectedFile = File(picked.path);
          _uploadResult = null;
          _validationResult = null;
          _errorMessage = null;
          _uploadProgress = 0;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not pick image: $e')),
        );
      }
    }
  }

  Future<void> _uploadAndProcess() async {
    if (_selectedFile == null) return;
    setState(() {
      _uploading = true;
      _errorMessage = null;
      _uploadProgress = 0;
      _uploadResult = null;
      _validationResult = null;
    });

    final api = context.read<AuthProvider>().apiService;
    try {
      // Simulate progress in absence of streaming progress callback
      for (int i = 1; i <= 5; i++) {
        await Future.delayed(const Duration(milliseconds: 200));
        if (mounted) setState(() => _uploadProgress = i * 0.1);
      }

      final result = await api.uploadISO(_selectedFile!);

      if (mounted) {
        setState(() {
          _uploadResult = result;
          _uploadProgress = 1.0;
        });
      }
    } on ApiException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<void> _runValidation() async {
    final isoId = _uploadResult?['id']?.toString();
    if (isoId == null) return;

    setState(() {
      _validating = true;
      _errorMessage = null;
    });

    final api = context.read<AuthProvider>().apiService;
    try {
      final result = await api.validateISO(isoId);
      if (mounted) setState(() => _validationResult = result);
    } on ApiException catch (e) {
      if (mounted) setState(() => _errorMessage = e.message);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _validating = false);
    }
  }

  void _reset() {
    setState(() {
      _selectedFile = null;
      _uploadResult = null;
      _validationResult = null;
      _errorMessage = null;
      _uploadProgress = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan ISO Document'),
        actions: [
          if (_selectedFile != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Reset',
              onPressed: _reset,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image picker area
            if (_selectedFile == null) ...[
              _PickerArea(onPick: _pickImage),
            ] else ...[
              _ImagePreview(file: _selectedFile!),
              const SizedBox(height: 12),

              // Upload button
              if (_uploadResult == null)
                ElevatedButton.icon(
                  onPressed: _uploading ? null : _uploadAndProcess,
                  icon: _uploading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.cloud_upload),
                  label: Text(_uploading ? 'Uploading…' : 'Upload & Process'),
                ),

              // Upload progress
              if (_uploading) ...[
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: _uploadProgress,
                    minHeight: 8,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${(_uploadProgress * 100).toInt()}%',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ],

            // Error message
            if (_errorMessage != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline,
                        color: theme.colorScheme.error, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(
                            color: theme.colorScheme.onErrorContainer),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // Extracted fields
            if (_uploadResult != null) ...[
              const SizedBox(height: 20),
              Text(
                'Extracted Fields',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _FieldRow(
                          'Filename',
                          _uploadResult!['filename']?.toString() ?? '-'),
                      _FieldRow(
                          'Line Number',
                          _uploadResult!['line_number']?.toString() ?? '-'),
                      _FieldRow(
                          'Pipe Size',
                          _uploadResult!['pipe_size']?.toString() ?? '-'),
                      _FieldRow(
                          'Spec', _uploadResult!['spec']?.toString() ?? '-'),
                      _FieldRow(
                          'Weld Count',
                          _uploadResult!['weld_count']?.toString() ?? '-'),
                      const Divider(),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Status'),
                          StatusBadge(
                            status: _uploadResult!['status']?.toString() ??
                                'pending',
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Validate button
              if (_validationResult == null)
                ElevatedButton.icon(
                  onPressed: _validating ? null : _runValidation,
                  icon: _validating
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.verified),
                  label:
                      Text(_validating ? 'Validating…' : 'Run Validation'),
                ),
            ],

            // Validation results
            if (_validationResult != null) ...[
              const SizedBox(height: 20),
              Row(
                children: [
                  Text(
                    'Validation Results',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(width: 8),
                  StatusBadge(
                    status: _validationResult!['overall_status']
                            ?.toString() ??
                        'pending',
                  ),
                ],
              ),
              const SizedBox(height: 8),
              _ValidationResultsList(result: _validationResult!),
            ],

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

class _PickerArea extends StatelessWidget {
  const _PickerArea({required this.onPick});

  final void Function(ImageSource) onPick;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: InkWell(
        onTap: () => onPick(ImageSource.gallery),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            children: [
              Icon(
                Icons.add_photo_alternate_outlined,
                size: 72,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 16),
              Text(
                'Select an ISO Document',
                style: theme.textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Tap to choose from gallery or use camera below',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 12,
                children: [
                  OutlinedButton.icon(
                    onPressed: () => onPick(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                  ),
                  ElevatedButton.icon(
                    onPressed: () => onPick(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ImagePreview extends StatelessWidget {
  const _ImagePreview({required this.file});

  final File file;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: Image.file(
        file,
        height: 220,
        width: double.infinity,
        fit: BoxFit.cover,
      ),
    );
  }
}

class _FieldRow extends StatelessWidget {
  const _FieldRow(this.label, this.value);

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
            width: 110,
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

class _ValidationResultsList extends StatelessWidget {
  const _ValidationResultsList({required this.result});

  final Map<String, dynamic> result;

  @override
  Widget build(BuildContext context) {
    final rules = result['rules'] as List<dynamic>? ?? [];

    if (rules.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: Text('No validation rules returned.')),
        ),
      );
    }

    return Column(
      children: rules.map((rule) {
        final r = rule as Map<String, dynamic>;
        final passed = r['passed'] == true || r['result'] == 'pass';
        return _RuleExpansionTile(rule: r, passed: passed);
      }).toList(),
    );
  }
}

class _RuleExpansionTile extends StatelessWidget {
  const _RuleExpansionTile({required this.rule, required this.passed});

  final Map<String, dynamic> rule;
  final bool passed;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final name = rule['rule']?.toString() ?? rule['name']?.toString() ?? 'Rule';
    final message = rule['message']?.toString();
    final details = rule['details']?.toString();

    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      color: passed ? Colors.green.shade50 : Colors.red.shade50,
      child: ExpansionTile(
        leading: Icon(
          passed ? Icons.check_circle : Icons.cancel,
          color: passed ? Colors.green.shade700 : Colors.red.shade700,
        ),
        title: Text(
          name,
          style: theme.textTheme.bodyMedium
              ?.copyWith(fontWeight: FontWeight.w600),
        ),
        trailing: StatusBadge(status: passed ? 'pass' : 'fail'),
        children: [
          if (message != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(message, style: theme.textTheme.bodySmall),
              ),
            ),
          if (details != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  details,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

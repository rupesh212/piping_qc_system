import 'package:flutter/material.dart';

/// Reusable status badge widget.
///
/// Supported statuses: pending, processed, error, valid, mismatch,
/// pass, fail, warning — plus a generic fallback for unknown values.
class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final config = _configFor(status.toLowerCase());

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: config.backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        config.label,
        style: TextStyle(
          color: config.textColor,
          fontSize: 11,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
    );
  }

  _BadgeConfig _configFor(String s) {
    switch (s) {
      case 'processed':
        return _BadgeConfig(
          label: 'Processed',
          backgroundColor: Colors.blue.shade100,
          textColor: Colors.blue.shade800,
        );
      case 'error':
        return _BadgeConfig(
          label: 'Error',
          backgroundColor: Colors.red.shade100,
          textColor: Colors.red.shade800,
        );
      case 'valid':
        return _BadgeConfig(
          label: 'Valid',
          backgroundColor: Colors.green.shade100,
          textColor: Colors.green.shade800,
        );
      case 'mismatch':
        return _BadgeConfig(
          label: 'Mismatch',
          backgroundColor: Colors.orange.shade100,
          textColor: Colors.orange.shade800,
        );
      case 'pass':
        return _BadgeConfig(
          label: 'Pass',
          backgroundColor: Colors.green.shade100,
          textColor: Colors.green.shade800,
        );
      case 'fail':
        return _BadgeConfig(
          label: 'Fail',
          backgroundColor: Colors.red.shade100,
          textColor: Colors.red.shade800,
        );
      case 'warning':
        return _BadgeConfig(
          label: 'Warning',
          backgroundColor: Colors.amber.shade100,
          textColor: Colors.amber.shade900,
        );
      case 'pending':
        return _BadgeConfig(
          label: 'Pending',
          backgroundColor: Colors.grey.shade200,
          textColor: Colors.grey.shade700,
        );
      default:
        return _BadgeConfig(
          label: s.isNotEmpty ? _capitalize(s) : 'Unknown',
          backgroundColor: Colors.grey.shade200,
          textColor: Colors.grey.shade700,
        );
    }
  }

  String _capitalize(String s) =>
      s[0].toUpperCase() + s.substring(1);
}

class _BadgeConfig {
  final String label;
  final Color backgroundColor;
  final Color textColor;

  const _BadgeConfig({
    required this.label,
    required this.backgroundColor,
    required this.textColor,
  });
}

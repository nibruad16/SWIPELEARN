import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:swipelearn/core/theme/app_theme.dart';
import 'package:swipelearn/widgets/shared_widgets.dart';

/// AddURLScreen — Paste a blog URL to generate a Knowledge Card.
/// Shows a URL input field, options to save as teacher, and a submit action.

class AddUrlScreen extends StatefulWidget {
  const AddUrlScreen({super.key});

  @override
  State<AddUrlScreen> createState() => _AddUrlScreenState();
}

class _AddUrlScreenState extends State<AddUrlScreen> {
  final _urlController = TextEditingController();
  bool _saveTeacher = false;
  bool _isLoading = false;
  bool _isSuccess = false;

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _pasteFromClipboard() async {
    final data = await Clipboard.getData('text/plain');
    if (data?.text != null) {
      _urlController.text = data!.text!;
      HapticFeedback.lightImpact();
    }
  }

  Future<void> _submitUrl() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) return;

    setState(() {
      _isLoading = true;
      _isSuccess = false;
    });

    // Simulate processing
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
      _isSuccess = true;
    });

    HapticFeedback.mediumImpact();

    // Reset after showing success
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      setState(() {
        _isSuccess = false;
        _urlController.clear();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 16),
          
          // Header
          const Text(
            'Add Knowledge',
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: AppColors.textPrimary,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Paste a blog URL to create a Knowledge Card',
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 32),

          // URL Input
          _buildUrlInput(),
          const SizedBox(height: 20),

          // Paste button
          GestureDetector(
            onTap: _pasteFromClipboard,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppColors.surfaceLight,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.surfaceBorder),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: const [
                  Icon(Icons.content_paste, size: 18, color: AppColors.primaryLight),
                  SizedBox(width: 8),
                  Text(
                    'Paste from clipboard',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: AppColors.primaryLight,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Save teacher toggle
          _buildTeacherToggle(),
          const SizedBox(height: 32),

          // Submit
          if (_isSuccess)
            _buildSuccessState()
          else
            GradientButton(
              label: 'Generate Knowledge Card',
              icon: Icons.auto_awesome,
              isLoading: _isLoading,
              onPressed: _submitUrl,
            ),
          const SizedBox(height: 32),

          // How it works
          _buildHowItWorks(),
        ],
      ),
    );
  }

  Widget _buildUrlInput() {
    return TextFormField(
      controller: _urlController,
      keyboardType: TextInputType.url,
      decoration: InputDecoration(
        hintText: 'https://blog.example.com/article',
        prefixIcon: const Icon(Icons.link, color: AppColors.textMuted),
        suffixIcon: _urlController.text.isNotEmpty
            ? IconButton(
                icon: const Icon(Icons.close, color: AppColors.textMuted),
                onPressed: () {
                  _urlController.clear();
                  setState(() {});
                },
              )
            : null,
      ),
      style: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 15,
        color: AppColors.textPrimary,
      ),
      onChanged: (_) => setState(() {}),
    );
  }

  Widget _buildTeacherToggle() {
    return GestureDetector(
      onTap: () {
        setState(() => _saveTeacher = !_saveTeacher);
        HapticFeedback.lightImpact();
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: _saveTeacher
              ? AppColors.primary.withOpacity(0.08)
              : AppColors.surfaceLight,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _saveTeacher ? AppColors.primary.withOpacity(0.3) : AppColors.surfaceBorder,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: _saveTeacher
                    ? AppColors.primary.withOpacity(0.15)
                    : AppColors.surface,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.school,
                color: _saveTeacher ? AppColors.primary : AppColors.textMuted,
                size: 20,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Follow this creator',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Auto-fetch their new posts as Knowledge Cards',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 12,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 48,
              height: 28,
              decoration: BoxDecoration(
                color: _saveTeacher ? AppColors.primary : AppColors.surfaceBorder,
                borderRadius: BorderRadius.circular(14),
              ),
              child: AnimatedAlign(
                duration: const Duration(milliseconds: 200),
                alignment: _saveTeacher ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  width: 24,
                  height: 24,
                  margin: const EdgeInsets.all(2),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuccessState() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.success.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.success.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.check_circle, color: AppColors.success, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'Card Created!',
                  style: TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: AppColors.success,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Swipe to your feed to see it',
                  style: TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 12,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHowItWorks() {
    return GlassContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'How it works',
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          _buildStep('1', 'Paste a blog URL', Icons.link),
          _buildStep('2', 'AI reads & extracts key insights', Icons.auto_awesome),
          _buildStep('3', 'Get a swipeable Knowledge Card', Icons.style),
        ],
      ),
    );
  }

  Widget _buildStep(String number, String text, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                number,
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryLight,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Icon(icon, size: 16, color: AppColors.textMuted),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontFamily: 'Inter',
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
